from app.infrastructure.logger import logger
from sqlalchemy.orm import Session
from typing import Optional

# --- ORM Models (Database Layer) ---
from app.infrastructure.models.auth.tenants import Tenant as ORMTenant
from app.infrastructure.models.auth.tenant_members import TenantMember as ORMTenantMember # ⚡ Added

# --- Domain Entities (Business Layer) ---
from app.domain.entities.tenant import Tenant as DomainTenant 
from app.domain.entities.tenant_member import TenantMember as DomainTenantMember         # ⚡ Added
from app.domain.interfaces.tenant_repository import ITenantRepository


class TenantRepository(ITenantRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_tenant(self, tenant: DomainTenant) -> DomainTenant:
        # Translate Domain data into the SQLAlchemy ORM model
        db_tenant = ORMTenant(
            id=tenant.id,
            slug=tenant.slug,
            name=getattr(tenant, 'name', None) or tenant.slug, 
            owner_id=tenant.owner_id,
            created_by=tenant.created_by,
            
            website_url=tenant.website_url,
            widget_api_key_hash=tenant.widget_api_key_hash,
            monthly_token_usage=tenant.monthly_token_usage
        )
        self.db.add(db_tenant)
        self.db.flush()
        self.db.refresh(db_tenant)
        
        # Map the DB generated ID back to the domain object
        tenant.id = str(db_tenant.id)
        
        return tenant
    
    def get_all_tenants(self) -> list[DomainTenant]:
        """
        Fetches all registered tenants from the global authentication database 
        and maps them into Domain Entities.
        """
        logger.info("Fetching all tenants from the global database configuration...")
        db_tenants = self.db.query(ORMTenant).all()
        
        return [
            DomainTenant(
                id=str(db.id),
                slug=db.slug,
                owner_id=str(db.owner_id),
                name=getattr(db, 'name', db.slug),
                created_by=str(getattr(db, 'created_by', db.owner_id))
            )
            for db in db_tenants
        ]

    def get_by_slug(self, slug: str) -> DomainTenant | None:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.slug == slug).first()
        if db_tenant:
            return DomainTenant(
                id=str(db_tenant.id),
                slug=db_tenant.slug,
                owner_id=str(db_tenant.owner_id),
                name=getattr(db_tenant, 'name', db_tenant.slug), 
                created_by=str(getattr(db_tenant, 'created_by', db_tenant.owner_id))
            )
        return None

    def get_by_id(self, tenant_id: str) -> DomainTenant | None:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.id == tenant_id).first()
        if db_tenant:
            return DomainTenant(
                id=str(db_tenant.id), 
                slug=db_tenant.slug, 
                owner_id=str(db_tenant.owner_id),
                name=getattr(db_tenant, 'name', db_tenant.slug),
                created_by=str(getattr(db_tenant, 'created_by', db_tenant.owner_id))
            )
        return None

    def get_by_owner_id(self, owner_id: str) -> Optional[DomainTenant]:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.owner_id == owner_id).first()
        
        if not db_tenant:
            return None
            
        return DomainTenant(
            id=str(db_tenant.id),
            name=db_tenant.name or "Unknown Tenant", 
            slug=db_tenant.slug,
            owner_id=str(db_tenant.owner_id),
            created_by=str(getattr(db_tenant, 'created_by', db_tenant.owner_id)) 
        )

    # ⚡======================================================⚡
    # ⚡ NEW METHOD: ADD MEMBER (Handles Junction Table)
    # ⚡======================================================⚡
    def add_member(self, membership: DomainTenantMember) -> DomainTenantMember:
        # 1. Map Domain -> ORM
        db_membership = ORMTenantMember(
            user_id=membership.user_id,
            tenant_id=membership.tenant_id,
            role=membership.role,
            is_active=membership.is_active
        )
        
        # 2. Save to Database
        self.db.add(db_membership)
        self.db.flush() 
        self.db.refresh(db_membership)
        
        # 3. Map DB ID back to Domain
        membership.id = str(db_membership.id)
        
        return membership