import logging
from sqlalchemy.orm import Session

# ⚡ 1. ALIAS YOUR IMPORTS TO PREVENT COLLISIONS
from app.infrastructure.models.auth.tenants import Tenant as ORMTenant
# Adjust this import path if your domain entity lives somewhere else!
from app.domain.entities.tenant import Tenant as DomainTenant 
from app.domain.interfaces.tenant_repository import ITenantRepository

class TenantRepository(ITenantRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_tenant(self, tenant: DomainTenant) -> DomainTenant:
        # ⚡ Translate Domain data into the SQLAlchemy ORM model
        db_tenant = ORMTenant(
            id=tenant.id,
            slug=tenant.slug,
            # ⚡ Fallback to slug if name is None to satisfy Postgres
            name=getattr(tenant, 'name', None) or tenant.slug, 
            owner_id=tenant.owner_id
        )
        
        self.db.add(db_tenant)
        self.db.flush()
        self.db.refresh(db_tenant)
        
        return tenant

    def get_by_slug(self, slug: str) -> DomainTenant | None:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.slug == slug).first()
        if db_tenant:
            # ⚡ 3. Map ORM Model back to Domain Entity before returning
            return DomainTenant(
                id=db_tenant.id,
                slug=db_tenant.slug,
                owner_id=db_tenant.owner_id
            )
        return None

    def get_by_id(self, tenant_id: str) -> DomainTenant | None:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.id == tenant_id).first()
        if db_tenant:
            return DomainTenant(
                id=db_tenant.id, 
                slug=db_tenant.slug, 
                owner_id=db_tenant.owner_id
            )
        return None

    def get_by_owner_id(self, owner_id: int) -> DomainTenant | None:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.owner_id == owner_id).first()
        if db_tenant:
            return DomainTenant(
                id=db_tenant.id, 
                slug=db_tenant.slug, 
                owner_id=db_tenant.owner_id
            )
        return None