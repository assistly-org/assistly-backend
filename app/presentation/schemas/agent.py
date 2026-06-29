# app/presentation/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional

class BotIntentRoute(BaseModel):
    """Classifies incoming user network strings for API routing."""
    intent: str = Field(..., description="Must be exactly one of: 'faq', 'lead_capture', 'add_to_cart', or 'book_appointment'.")
    confidence: float = Field(..., description="Confidence metrics score tightly ranging from 0.0 to 1.0.")

class LeadCaptureExtractionSchema(BaseModel):
    """Pydantic model specifically used to parse JSON structures from Gemini."""
    full_name: Optional[str] = Field(None, description="The customer's name.")
    phone: Optional[str] = Field(None, description="The customer's phone number.")
    email: Optional[str] = Field(None, description="The customer's email address.")
    extracted_notes: Optional[str] = Field(None, description="User intent constraints or preferences.")
