from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User:
    email: str
    password_hash: str
    auth_provider: str = "local"
    id: Optional[int] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Core Business Logic: A user can change their password
    def update_password(self, new_hash: str) -> None:
        self.password_hash = new_hash

    # Core Business Logic: A user can be deactivated
    def deactivate(self) -> None:
        self.is_active = False