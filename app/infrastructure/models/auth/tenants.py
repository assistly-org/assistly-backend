import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.database import Base

if TYPE_CHECKING:
    from .users import User

class Tenant(Base):
    """The monolithic absolute root anchor controlling data visibility scopes."""
    __tablename__ = "tenant" 
    __table_args__ = {'schema': 'assistly_auth'} # Enforce global schema

    # --- 1. CORE IDENTIFIERS ---
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # --- 2. SYSTEM STATUS ---
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    plan_tier: Mapped[str] = mapped_column(String(50), default="free", nullable=False)

    # --- 3. ROBUST DEEP BILLING INTERFACES (STRIPE) ---
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subscription_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subscription_cycle_anchor: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_start_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_end_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- 4. DATA OWNERSHIP ---
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assistly_auth.users.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("assistly_auth.users.id", ondelete="SET NULL"),
        nullable=True
    )

    # --- 5. SYSTEM TEMPORAL TEMPLATES ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- RELATIONSHIPS ---
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_tenants",
        foreign_keys=[owner_id]
    )
    
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_tenants",
        foreign_keys=[created_by]
    )