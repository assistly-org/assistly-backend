import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.database import Base

if TYPE_CHECKING:
    from .users import User
    from .tenants import Tenant

class TenantMember(Base):
    """Junction table linking Users to Tenants with workspace-specific roles."""
    __tablename__ = "tenant_members"
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uix_user_tenant_membership"),
        {'schema': 'assistly_auth'}
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: f"mem-{uuid.uuid4().hex[:16]}")
    
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("assistly_auth.users.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("assistly_auth.tenants.id", ondelete="CASCADE"), nullable=False)

    # ⚡ Workspace-Specific Role!
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False) 
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="memberships")
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="members")