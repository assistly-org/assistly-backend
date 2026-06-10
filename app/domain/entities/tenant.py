from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Tenant:
    name: str
    slug: str
    owner_id: int
    created_by: int
    id: Optional[int] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Core Business Logic: A tenant can be renamed, but the slug (subdomain) NEVER changes
    def rename_company(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Company name cannot be empty")
        self.name = new_name

    # Core Business Logic: Suspending a tenant for non-payment
    def suspend(self) -> None:
        self.is_active = False