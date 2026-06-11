
from sqlalchemy import Column, String, DateTime, Integer, Numeric
from sqlalchemy.sql import func
from app.infrastructure.db.database import (
    TenantBase,
)  # Adjust this import if your Base is located elsewhere!


class Booking(TenantBase):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    customer_name = Column(String(255), nullable=False)
    service_name = Column(String(255), nullable=False)
    service_type = Column(String(255), nullable=False)
    status = Column(
        String(50), default="pending"
    )  # e.g., pending, confirmed, cancelled
    total_amount = Column(Numeric(10, 2), nullable=True)
    discount_amount = Column(Numeric(10, 2), nullable=True)
    # Automatically track when the booking was created

    created_at = Column(DateTime(timezone=True), server_default=func.now())


