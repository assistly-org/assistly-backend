# app/domain/repositories/tenant.py
from abc import ABC, abstractmethod
from typing import Optional
# from app.infrastructure.models.auth.tenants import Tenant
from app.domain.entities.tenant import Tenant

class ITenantRepository(ABC):
    
    @abstractmethod
    def create_tenant(self, tenant: Tenant) -> Tenant:
        """Stages a new tenant record into the data store memory."""
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Retrieves a tenant by their unique subdomain workspace slug."""
        pass

    @abstractmethod
    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Retrieves a tenant by their unique primary key ID."""
        pass

    @abstractmethod
    def get_by_owner_id(self, owner_id: int) -> Optional[Tenant]:
        """Retrieves a tenant associated with a specific owner's user ID."""
        pass