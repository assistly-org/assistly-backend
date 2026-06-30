from .tenants import Tenant
from .tenant_members import TenantMember
import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.database import Base

if TYPE_CHECKING:
    from .tenants import Tenant
    from .addresses import Address
    from .tenant_members import TenantMember


class User(Base):
    """Global Identity Table."""
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "(auth_provider = 'local' AND password_hash IS NOT NULL) OR (auth_provider != 'local')",
            name="chk_local_auth_requires_password"
        ),
        {'schema': 'assistly_auth'}
    )

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"usr-{uuid.uuid4().hex[:16]}")
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    auth_provider: Mapped[str] = mapped_column(
        String(50), default="local", nullable=False)
    oauth_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)

    # ⚡ REPLACED GLOBAL ROLE
    is_system_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)  # Fixed typo and default
    last_active_tenant_subdomain: Mapped[Optional[str]
                                    ] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    owned_tenants: Mapped[List["Tenant"]] = relationship(
        "Tenant", back_populates="owner", foreign_keys="Tenant.owner_id")
    created_tenants: Mapped[List["Tenant"]] = relationship(
        "Tenant", back_populates="creator", foreign_keys="Tenant.created_by")
    addresses: Mapped[List["Address"]] = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan")
    # ⚡ NEW: Link to workspace memberships
    memberships: Mapped[List["TenantMember"]] = relationship(
        "TenantMember", back_populates="user", cascade="all, delete-orphan")
