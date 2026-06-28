# assistly-backend/app/infrastructure/repositories/agent_repository.py
import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text

from sqlalchemy.dialects.postgresql import insert

from app.domain.interfaces.agent_repository import IAgentRepository
from app.domain.entities.agent import LeadCapture
from app.infrastructure.models.agent.agent import (
    OmnichannelSessionModel,
    LeadCaptureModel,
)

# Add this line at the top imports section of agent_repository.py
from app.infrastructure.db.tenant_context import get_tenant_schema


class AgentRepository(IAgentRepository):
    """
    SQLAlchemy implementation of the Agent Data Access Layer.
    Enforces tenant_id and bot_id checking across all database operations.
    """

    def _apply_active_tenant_schema(self) -> None:
        """Dynamically binds the active database connection to the current schema."""
        active_schema = (
            get_tenant_schema()
        )  # Automatically reads 'tenant_book' or 'tenant_mobilemart'

        self.db.execute(text(f"SET search_path TO {active_schema}, public;"))
        self.db.commit()

    def __init__(self, db_session: Session):
        self.db = db_session

    async def create_omnichannel_session(
        self,
        session_id: str,
        tenant_id: UUID,
        bot_id: UUID,
        primary_phone: Optional[str],
        channel_source: str,
    ) -> Dict[str, Any]:

        self._apply_active_tenant_schema()

        """
        Creates a new chat session state or retrieves it if it already exists.
        Uses a PostgreSQL upsert to gracefully handle reconnections.
        """
        # Prepare the update/insert statement
        stmt = insert(OmnichannelSessionModel).values(
            session_id=session_id,
            tenant_id=tenant_id,
            bot_id=bot_id,
            primary_phone=primary_phone,
            channel_source=channel_source,
            active_context={},
            updated_at=datetime.datetime.utcnow(),
        )

        # If session_id already exists, just touch the updated_at timestamp
        # to preserve the existing chat history and context
        stmt = stmt.on_conflict_do_update(
            index_elements=["session_id"],
            set_={
                "updated_at": datetime.datetime.utcnow(),
                "primary_phone": primary_phone or OmnichannelSessionModel.primary_phone,
            },
        )

        self.db.execute(stmt)
        self.db.commit()

        return {
            "session_id": session_id,
            "tenant_id": str(tenant_id),
            "bot_id": str(bot_id),
            "status": "synchronized",
        }

    async def save_lead_capture(
        self, tenant_id: UUID, bot_id: UUID, session_id: str, payload: LeadCapture
    ) -> Dict[str, Any]:
        
        
        self._apply_active_tenant_schema()

        """
        Persists a newly captured customer lead into the business dashboard storage.
        """
        # ✅ FIXED: Safely look into metadata_fields dictionary mapping instead of payload root
        extracted_notes = None
        if payload.metadata_fields and isinstance(payload.metadata_fields, dict):
            extracted_notes = payload.metadata_fields.get("extracted_notes")

        metadata_content = (
            {"extracted_notes": extracted_notes} if extracted_notes else {}
        )

        db_lead = LeadCaptureModel(
            tenant_id=tenant_id,
            bot_id=bot_id,
            session_id=session_id,
            full_name=payload.full_name,
            phone=payload.phone,
            email=payload.email,
            metadata_fields=metadata_content,
        )

        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)

        return {
            "lead_id": str(db_lead.id),
            "status": "saved_successfully",
            "timestamp": db_lead.created_at.isoformat(),
        }

    async def get_session_context(
        self, session_id: str, tenant_id: UUID
    ) -> Optional[Dict[str, Any]]:
        self._apply_active_tenant_schema()

        """
        Fetches short-term chatbot memory logs for a specific user thread.
        Includes verification of tenant_id to block multi-tenant data bleed.
        """
        session_record = (
            self.db.query(OmnichannelSessionModel)
            .filter(
                OmnichannelSessionModel.session_id == session_id,
                OmnichannelSessionModel.tenant_id == tenant_id,
            )
            .first()
        )

        if not session_record:
            return None

        return {
            "session_id": session_record.session_id,
            "bot_id": str(session_record.bot_id),
            "channel_source": session_record.channel_source,
            "active_context": session_record.active_context,
        }
