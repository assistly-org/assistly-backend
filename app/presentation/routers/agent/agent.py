# app/presentation/routers/agent.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db

# Import Clean Architecture layers
from app.application.use_cases.agent.process_action import ProcessAgentActionUseCase
from app.infrastructure.repositories.agent_repository import AgentRepository

router = APIRouter(prefix="/agent", tags=["AI Agent Action Engine"])

# The strict contractual model Saniya's frontend widget must send over the network
class ChatIncomingRequest(BaseModel):
    message: str
    tenant_id: UUID
    bot_id: UUID
    session_id: str
    channel_source: str = "web_widget"  # Defaults to web widget, can be 'whatsapp'


@router.post("/process", status_code=status.HTTP_200_OK)
async def process_chat_message(
    payload: ChatIncomingRequest,
    db: Session = Depends(get_db),  # This session is schema-switched by your team's middleware
):
    """
    Public REST API endpoint for Assistly bots. Receives incoming chat strings from widgets,
    routes them to the Gemini Action Engine, and interacts with the schema-isolated data layer.
    """
    # 1. Instantiate the Repository implementation passing the current active schema DB session
    agent_repo = AgentRepository(db_session=db)

    # 2. Inject the repo implementation directly into the Use Case (Dependency Injection)
    use_case = ProcessAgentActionUseCase(agent_repo=agent_repo)

    # 3. Execute the core business logic orchestration block 
    # (The try/except guardrail inside process_action.py will handle database warnings safely!)
    result = await use_case.execute(
        message=payload.message,
        tenant_id=payload.tenant_id,
        bot_id=payload.bot_id,
        session_id=payload.session_id,
        channel_source=payload.channel_source,
    )

    return result
