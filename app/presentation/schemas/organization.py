from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TenantSummary(BaseModel):
    id: str
    name: str
    subdomain: str
    status: str
    plan_tier: str
    is_active: bool
    website_url: Optional[str] = None
    owner_name : str
    created_by : str

    # FIX: Make this Optional so it doesn't crash if the DB returns None
    created_at: Optional[datetime] = None

    logo_url: Optional[str] = None

    class Config:
        from_attributes = True

        # i need to solve in here a issue like about the created an logourl


# The class that got accidentally dropped!
class TenantListResponse(BaseModel):
    tenants: List[TenantSummary]
    total: int
