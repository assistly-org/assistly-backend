from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class User:
    email: str
    password_hash: Optional[str] = None # Optional because OAuth users might not have one
    auth_provider: str = "local"
    oauth_id: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    id: Optional[str] = None 
    is_system_admin: bool = False
    is_active: bool = True
    is_verified: bool = False
    last_active_tenant_subdomain: Optional[str] = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # --- Core Business Logic ---
    def update_password(self, new_hash: str) -> None:
        self.password_hash = new_hash

    def deactivate(self) -> None:
        self.is_active = False

    def verify_account(self) -> None:
        """Mark the user as verified after OTP success."""
        self.is_verified = True

    def update_last_workspace(self, tenant_subdomain: str) -> None:
        """Track the last workspace they logged into for seamless UX."""
        self.last_active_tenant_subdomain = tenant_subdomain