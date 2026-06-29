# app/domain/entities/agent.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

@dataclass
class OmnichannelSession:
    session_id: str
    tenant_id: str
    bot_id: str
    channel_source: str # 'web_widget' or 'whatsapp'
    primary_phone: Optional[str] = None
    active_context: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class LeadCapture:
    tenant_id: str
    bot_id: str
    session_id: str
    id: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    metadata_fields: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
