# app/infrastructure/repositories/tenant.py
from sqlalchemy.orm import Session
from app.infrastructure.models.auth.tenants import Tenant
from app.domain.repositories.tenant import ITenantRepository  # <-- Import the interface

class TenantRepository(ITenantRepository):  # <-- Inherit from the interface
    def __init__(self, db: Session):
        self.db = db

    def create_tenant(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        self.db.flush()  # Flushes to get the ID generated, but doesn't commit yet!
        self.db.refresh(tenant)
        return tenant

    def get_by_slug(self, slug: str) -> Tenant | None:
        return (
            self.db.query(Tenant)
            .filter(Tenant.slug == slug)
            .first()
        )

    def get_by_id(self, tenant_id: str) -> Tenant | None:
        return (
            self.db.query(Tenant)
            .filter(Tenant.id == tenant_id)
            .first()
        )
        
    def get_by_owner_id(self, owner_id: int) -> Tenant | None:
        return (
            self.db.query(Tenant)
            .filter(Tenant.owner_id == owner_id)
            .first()
        )