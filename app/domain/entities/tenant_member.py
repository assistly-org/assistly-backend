# app/domain/entities/tenant_member.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class TenantMember:
    user_id: str
    tenant_id: str
    role: str = "member"  # 'owner', 'admin', 'editor', 'viewer'
    
    id: Optional[str] = None
    is_active: bool = True
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def promote_to_admin(self) -> None:
        self.role = "admin"

    def revoke_access(self) -> None:
        self.is_active = False