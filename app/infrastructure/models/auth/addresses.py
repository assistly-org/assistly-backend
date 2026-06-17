import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.database import Base

if TYPE_CHECKING:
    from .users import User


class Address(Base):
    """Global Address Table for Users."""
    __tablename__ = "addresses"
    __table_args__ = {'schema': 'assistly_auth'}

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"adr-{uuid.uuid4().hex[:16]}")

    user_id: Mapped[str] = mapped_column(ForeignKey(
        "assistly_auth.users.id", ondelete="CASCADE"), nullable=False)

    street_1: Mapped[str] = mapped_column(String(255), nullable=False)
    street_2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state_province: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text(
        "CURRENT_TIMESTAMP"), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # ⚡ FIXED: Deleted_at is now Optional and defaults to None!
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="addresses")
