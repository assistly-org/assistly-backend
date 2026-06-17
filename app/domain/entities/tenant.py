from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class Tenant:
    name: str
    slug: str
    owner_id: str
    
    id: Optional[str] = None
    logo_url: Optional[str] = None
    created_by: Optional[str] = None
    website_url: Optional[str] = None          
    widget_api_key_hash: Optional[str] = None  
    monthly_token_usage: int = 0               

    # --- Billing fields ---
    status: str = "active"
    is_active: bool = True
    plan_tier: str = "free"
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

    def suspend_workspace(self) -> None:
        """Suspend access to the workspace (e.g., for non-payment or TOS violation)."""
        self.is_active = False
        self.status = "suspended"

    def upgrade_plan(self, new_tier: str) -> None:
        """Upgrade the workspace billing tier."""
        valid_tiers = ["free", "pro", "enterprise"]
        if new_tier not in valid_tiers:
            raise ValueError(f"Invalid plan tier. Must be one of: {valid_tiers}")
        self.plan_tier = new_tier