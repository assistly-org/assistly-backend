
from sqlalchemy import Column, String, DateTime, Integer , Numeric
from sqlalchemy.sql import func
from app.infrastructure.db.database import (
    TenantBase,
)  # Adjust this import if your Base is located elsewhere!


class Booking(TenantBase):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False)
    service_name = Column(String(255), nullable=False)
    service_type = Column(String(255), nullable=False)
    status = Column(
        String(50), default="pending"
    )  # e.g., pending, confirmed, cancelled

    # Automatically track when the booking was created
    total_amount = Column(Numeric(10, 2), nullable=True)
    
    discount_amount = Column(Numeric(10, 2), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
