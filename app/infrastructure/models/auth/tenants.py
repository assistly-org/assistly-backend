import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.database import Base

if TYPE_CHECKING:
    from .users import User
    from .tenant_members import TenantMember


class Tenant(Base):
    """The monolithic absolute root anchor controlling data visibility scopes."""
    __tablename__ = "tenants"  
    __table_args__ = {'schema': 'assistly_auth'}

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"tnt-{uuid.uuid4().hex[:16]}")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    plan_tier: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False)

    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)
    subscription_status: Mapped[Optional[str]
                                ] = mapped_column(String(50), nullable=True)
    subscription_cycle_anchor: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    trial_start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    trial_end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)

    owner_id: Mapped[str] = mapped_column(ForeignKey(
        "assistly_auth.users.id", ondelete="RESTRICT"), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(ForeignKey(
        "assistly_auth.users.id", ondelete="SET NULL"), nullable=True)

    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)

    monthly_token_usage: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False)  
    widget_api_key_hash: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text(
        "CURRENT_TIMESTAMP"), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)

    owner: Mapped["User"] = relationship(
        "User", back_populates="owned_tenants", foreign_keys=[owner_id])
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_tenants", foreign_keys=[created_by])

    # ⚡ NEW: Link to workspace members
    members: Mapped[List["TenantMember"]] = relationship(
        "TenantMember", back_populates="tenant", cascade="all, delete-orphan")
