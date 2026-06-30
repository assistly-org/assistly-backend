from app.infrastructure.logger import logger
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import joinedload
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
            subdomain=tenant.subdomain,
            # ⚡ Fallback to subdomain if name is None to satisfy Postgres
            name=getattr(tenant, 'name', None) or tenant.subdomain, 
            owner_id=tenant.owner_id,
            created_by=tenant.created_by,
            
            website_url=tenant.website_url,
            widget_api_key_hash=tenant.widget_api_key_hash,
            monthly_token_usage=tenant.monthly_token_usage
        )
        self.db.add(db_tenant)
        self.db.flush()
        self.db.refresh(db_tenant)
        
        # ⚡ THE MISSING LINK: Manually assign the generated DB ID back to your Domain Entity
        tenant.id = str(db_tenant.id)
        
        # Now when you return it to the Service, it has the ID!
        return tenant
    
    def delete_tenant_and_schema(self, tenant_id: str) -> bool:
        """
        Deletes the tenant schema and the ORM record.
        Takes a tenant_id (string) instead of the Domain model.
        """
        # 1. Fetch the ORM model (SQLAlchemy needs this to delete it)
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.id == tenant_id).first()
        
        if not db_tenant:
            logger.warning(f"Repo: Tenant with ID {tenant_id} not found.")
            return False

        schema_name = f"tenant_{db_tenant.subdomain}"
        
        try:
            # 2. Drop Schema
            logger.info(f"Repo: Dropping schema {schema_name}")
            self.db.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
            
            # 3. Delete Record (Passing the ORM model, NOT the domain model)
            logger.info(f"Repo: Deleting tenant record {db_tenant.id}")
            self.db.delete(db_tenant)
            
            # 4. Commit Transaction
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Repo: Database transaction failed. Rolled back. Error: {e}")
            raise e
    
    
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
                subdomain=db.subdomain,
                owner_id=str(db.owner_id),
                name=getattr(db, 'name', db.subdomain),
                created_by=str(getattr(db, 'created_by', db.owner_id))
            )
            for db in db_tenants
        ]

    def get_by_subdomain(self, subdomain: str) -> DomainTenant | None:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.subdomain == subdomain).first()
        if db_tenant:
            return DomainTenant(
                id=str(db_tenant.id),
                subdomain=db_tenant.subdomain,
                owner_id=str(db_tenant.owner_id),
                name=getattr(db_tenant, 'name', db_tenant.subdomain), 
                created_by=str(getattr(db_tenant, 'created_by', db_tenant.owner_id))
            )
        return None

    def get_by_id(self, tenant_id: str) -> DomainTenant | None:
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.id == tenant_id).first()
        if db_tenant:
            return DomainTenant(
                id=str(db_tenant.id), 
                subdomain=db_tenant.subdomain, 
                owner_id=str(db_tenant.owner_id),
                name=getattr(db_tenant, 'name', db_tenant.subdomain),
                created_by=str(getattr(db_tenant, 'created_by', db_tenant.owner_id))
            )
        return None

    def get_by_owner_id(self, owner_id: str) -> Optional[DomainTenant]:
        # 1. Fetch the ORM model from the database
        db_tenant = self.db.query(ORMTenant).filter(ORMTenant.owner_id == owner_id).first()
        
        if not db_tenant:
            return None
        # 2. Map ORM model -> Domain Entity
        # ⚡ Ensure every single argument required by the DomainTenant dataclass is here!
        return DomainTenant(
            id=str(db_tenant.id),
            name=db_tenant.name or "Unknown Tenant", 
            subdomain=db_tenant.subdomain,
            owner_id=str(db_tenant.owner_id),
            created_by=str(getattr(db_tenant, 'created_by', db_tenant.owner_id)) 
        )

    def get_all_by_owner_id(self, owner_id: str) -> list[DomainTenant]:
        """
        Fetches ALL active tenants owned by a specific user, including the owner's name.
        """
        db_tenants = (
            self.db.query(ORMTenant)
            .options(joinedload(ORMTenant.owner))  # ⚡ Eagerly load the user data
            .filter(
                ORMTenant.owner_id == owner_id,
                ORMTenant.deleted_at.is_(None),
            )
            .order_by(ORMTenant.created_at.desc())
            .all()
        )

        return [
            DomainTenant(
                id=str(tenant.id),
                name=tenant.name,
                subdomain=tenant.subdomain,
                owner_id=str(tenant.owner_id),
                # ⚡ Safely grab the owner's name if the user exists
                owner_name=tenant.owner.name if tenant.owner else None,
                created_by=(
                    str(tenant.created_by)
                    if tenant.created_by
                    else str(tenant.owner_id)
                ),
                status=tenant.status,
                plan_tier=tenant.plan_tier,
                is_active=tenant.is_active,
                created_at=tenant.created_at,
                logo_url=tenant.logo_url,
                website_url=tenant.website_url
            )
            for tenant in db_tenants
        ]

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