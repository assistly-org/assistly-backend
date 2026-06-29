# app/application/use_cases/agent/process_action.py
import os
from typing import Dict, Any
from uuid import UUID
from google import genai
from google.genai import types
from google.genai.errors import ServerError  # ⚡ IMPORT THIS

from app.domain.entities.agent import LeadCapture
from app.domain.interfaces.agent_repository import IAgentRepository
from app.presentation.schemas.agent import BotIntentRoute, LeadCaptureExtractionSchema


class ProcessAgentActionUseCase:
    def __init__(self, agent_repo: IAgentRepository):
        self.repo = agent_repo
        self.ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    async def execute(
        self,
        message: str,
        tenant_id: UUID,
        bot_id: UUID,
        session_id: str,
        channel_source: str,
    ) -> Dict[str, Any]:

        # 1. Initialize or touch the session state inside the active connection
        await self.repo.create_omnichannel_session(
            session_id=session_id,
            tenant_id=tenant_id,
            bot_id=bot_id,
            primary_phone=None,
            channel_source=channel_source,
        )

        # 1.5 READ the existing session context from the database to load memory
        session_record = await self.repo.get_session_context(
            session_id=session_id, tenant_id=tenant_id
        )

        # Extract current state indicators (defaulting to idle if clean)
        current_state = (
            session_record.get("active_context", {}).get("state", "idle")
            if session_record
            else "idle"
        )
        current_action = (
            session_record.get("active_context", {}).get("action")
            if session_record
            else None
        )
        saved_slots = (
            session_record.get("active_context", {}).get("slots", {})
            if session_record
            else {}
        )

        system_router_prompt = (
            "You are the structural intent routing chip for Assistly. Evaluate the user's message "
            "and classify their core intent into the required JSON schema structure."
        )

        try:
            # 2. Call Gemini to classify intent
            response = self.ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=system_router_prompt,
                    response_mime_type="application/json",
                    response_schema=BotIntentRoute,
                    temperature=0.0,
                ),
            )
            routing_result = BotIntentRoute.model_validate_json(response.text)

        except ServerError as e:
            # ⚡ THE AI FALLBACK GUARDRAIL: Catches Google's 503 spikes gracefully
            if e.status_code == 503:
                return {
                    "intent": "fallback_router",
                    "ai_response": "I am experiencing a slight delay processing your request. Please try your message once more.",
                    "action_status": {
                        "status": "upstream_llm_overloaded",
                        "error_details": "Gemini 2.5 Flash free tier is experiencing temporary high demand spikes.",
                    },
                    "ui_trigger": "show_soft_retry_button",
                }
            raise e

        # 3. Handle a Lead Capture Action Engine flow if Gemini succeeded
        if routing_result.intent == "lead_capture" and routing_result.confidence > 0.7:
            try:
                extracted_data = self._extract_lead_fields(message)
            except ServerError:
                # Fallback if the second sub-call hits a 503 spike as well
                return {
                    "intent": "lead_capture_failed",
                    "ai_response": "I see you want to register. I am having trouble connecting right now. Please try again.",
                    "action_status": {"status": "extraction_api_unavailable"},
                    "ui_trigger": "render_manual_lead_form",  # 💡 Smart UI fallback!
                }

                # 3.5 Merge newly extracted fields with previously saved database slots
            merged_slots = {
                "full_name": extracted_data.full_name or saved_slots.get("full_name"),
                "phone": extracted_data.phone or saved_slots.get("phone"),
                "email": extracted_data.email or saved_slots.get("email"),
                "extracted_notes": extracted_data.extracted_notes
                or saved_slots.get("extracted_notes"),
            }

            # Map the combined fields into the clean Domain Entity
            domain_lead = LeadCapture(
                tenant_id=str(tenant_id),
                bot_id=str(bot_id),
                session_id=session_id,
                full_name=merged_slots["full_name"],
                phone=merged_slots["phone"],
                email=merged_slots["email"],
                metadata_fields=(
                    {"extracted_notes": merged_slots["extracted_notes"]}
                    if merged_slots["extracted_notes"]
                    else {}
                ),
            )
            # 3.7 Identify any critical parameters that are still unfulfilled
            missing_slots = [
                key
                for key, val in merged_slots.items()
                if val is None and key != "extracted_notes"
            ]

            if missing_slots:
                # Calculate the immediate next field to collect
                target_field = missing_slots[0]
                friendly_field_name = target_field.replace("_", " ")

                # Persist the current snapshot memory down to the session
                await self.repo.update_session_state(
                    session_id=session_id,
                    state="slot_filling",
                    action="lead_capture",
                    context_data={"slots": merged_slots},
                )

                return {
                    "intent": "lead_capture",
                    "ai_response": f"Thanks! Could you please tell me your {friendly_field_name}?",
                    "action_status": {
                        "status": "slot_filling",
                        "awaiting": target_field,
                    },
                    "ui_trigger": f"focus_{target_field}",
                }

            db_save_result = await self.repo.save_lead_capture(
                tenant_id=tenant_id,
                bot_id=bot_id,
                session_id=session_id,
                payload=domain_lead,
            )

            return {
                "intent": "lead_capture",
                "ai_response": "Perfect! I have recorded your contact details. Our representative will contact you shortly.",
                "action_status": db_save_result,
                "ui_trigger": "render_lead_success_ui",
            }

        return {
            "intent": "faq",
            "ai_response": None,
            "action_status": {"status": "trigger_hybrid_vector_search"},
            "ui_trigger": "show_typing_indicator",
        }

    def _extract_lead_fields(self, message: str) -> LeadCaptureExtractionSchema:
        response = self.ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Extract context elements from: {message}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=LeadCaptureExtractionSchema,
                temperature=0.0,
            ),
        )
        return LeadCaptureExtractionSchema.model_validate_json(response.text)
