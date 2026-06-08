import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.database import Base

if TYPE_CHECKING:
    from .tenants import Tenant
    from .addresses import Address


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

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)

    # OAuth Integration Fields
    auth_provider: Mapped[str] = mapped_column(String(
        50), default="local", nullable=False)  # e.g., 'local', 'google', 'github'
    oauth_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Made Optional to support users who ONLY log in via OAuth
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)

    role: Mapped[str] = mapped_column(
        String(50), default="tenant_admin", nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    owned_tenants: Mapped[List["Tenant"]] = relationship(
        "Tenant",
        back_populates="owner",
        foreign_keys="Tenant.owner_id"
    )

    created_tenants: Mapped[List["Tenant"]] = relationship(
        "Tenant",
        back_populates="creator",
        foreign_keys="Tenant.created_by"
    )

    addresses: Mapped[List["Address"]] = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan"
    )
