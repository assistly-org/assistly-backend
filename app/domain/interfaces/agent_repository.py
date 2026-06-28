# assistly-backend/app/domain/interfaces/agent_repository.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from uuid import UUID
from app.domain.entities.agent import LeadCapture

class IAgentRepository(ABC):
    """
    Abstract interface for Agent operations. 
    Enforces that any database implementation must accept tenant_id and bot_id.
    """
    
    @abstractmethod
    async def create_omnichannel_session(
        self, 
        session_id: str, 
        tenant_id: UUID, 
        bot_id: UUID, 
        primary_phone: Optional[str], 
        channel_source: str
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def save_lead_capture(
        self, 
        tenant_id: UUID, 
        bot_id: UUID, 
        session_id: str, 
        payload: LeadCapture
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_session_context(self, session_id: str, tenant_id: UUID) -> Optional[Dict[str, Any]]:
        pass
