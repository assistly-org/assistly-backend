from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.tenant import Tenant as DomainTenant

class ITenantRepository(ABC):

    @abstractmethod
    def create_tenant(self, tenant: DomainTenant) -> DomainTenant:
        """Stages a new tenant record into the data store memory."""
        pass

    @abstractmethod
    def get_all_tenants(self) -> list[DomainTenant]:
        """Fetch all tenants from storage."""
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[DomainTenant]:
        """Retrieves a tenant by their unique subdomain workspace slug."""
        pass

    @abstractmethod
    def get_by_id(self, tenant_id: str) -> Optional[DomainTenant]:
        """Retrieves a tenant by their unique primary key ID."""
        pass

    @abstractmethod
    def get_by_owner_id(self, owner_id: str) -> Optional[DomainTenant]:
        """Retrieves a single tenant associated with a specific owner's user ID."""
        pass

    @abstractmethod
    def get_all_by_owner_id(self, owner_id: str) -> list[DomainTenant]:
        """Fetches ALL active tenants owned by a specific user."""
        pass