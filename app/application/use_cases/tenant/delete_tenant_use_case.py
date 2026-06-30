# app/application/use_cases/delete_tenant_use_case.py
from app.domain.interfaces.tenant_repository import ITenantRepository
from app.infrastructure.logger import logger

class DeleteTenantUseCase:
    def __init__(self, tenant_repo: ITenantRepository):
        self.tenant_repo = tenant_repo

    def execute(self, tenant_id: str, current_user_id: str) -> bool:
        # 1. Check if tenant exists
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("Organization not found.")
            
        # 2. Security Check: Ensure the user trying to delete it is the owner
        if tenant.owner_id != current_user_id:
            raise PermissionError("You do not have permission to delete this organization.")

        # 3. Execute deletion
        success = self.tenant_repo.delete_tenant_and_schema(tenant_id)
        if success:
            logger.info(f"Service: Successfully deleted tenant {tenant_id}")
            return True
            
        return False