
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.infrastructure.db.database import TenantBase

class OmnichannelSessionModel(TenantBase):
    __tablename__ = "omnichannel_sessions"

    session_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), index=True)
    bot_id = Column(UUID(as_uuid=True), index=True)
    primary_phone = Column(String(20), nullable=True)
    channel_source = Column(String(50), nullable=False)
    
    # ⚡ CRITICAL: Ensure these match your migration file fields!
    conversation_state = Column(String(30), default="idle", nullable=False)
    active_action = Column(String(50), nullable=True)
    
    active_context = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, nullable=True)

class LeadCaptureModel(TenantBase):
    __tablename__ = "lead_captures"

    id = Column(String(50), primary_key=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), index=True)
    bot_id = Column(UUID(as_uuid=True), index=True)
    session_id = Column(String, ForeignKey("omnichannel_sessions.session_id", ondelete="SET NULL"), nullable=True)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    metadata_fields = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime, nullable=True)
