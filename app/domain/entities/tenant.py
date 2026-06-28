from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class Tenant:
    # 1. CORE IDENTIFIERS (Updated to str to support your DB UUIDs)
    name: str
    slug: str
    owner_id: str
    created_by: Optional[str] = None
    id: Optional[str] = None
    
    
    website_url: Optional[str] = None
    widget_api_key_hash: Optional[str] = None
    monthly_token_usage: int = 0
    
    # 2. MISSING FIELDS (Added to satisfy Pydantic and your DB)
    status: str = "active"
    plan_tier: str = "free"
    is_active: bool = True
    logo_url: Optional[str] = None
    created_at: Optional[datetime] = None

    # --- Billing fields ---
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_price_id: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_cycle_anchor: Optional[datetime] = None
    trial_start_at: Optional[datetime] = None
    trial_end_at: Optional[datetime] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False

    # --- Core Business Logic ---
    def rename_company(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Company name cannot be empty")
        self.name = new_name

    # Core Business Logic: Suspending a tenant for non-payment
    def suspend(self) -> None:
        self.status = "suspended"
        self.is_active = False  
