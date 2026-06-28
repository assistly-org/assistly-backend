# app/application/use_cases/organization/list_tenants.py
import logging
from fastapi import HTTPException
from app.presentation.schemas.organization import TenantListResponse, TenantSummary

logger = logging.getLogger("assistly")


class ListTenantsService:
    def __init__(self, tenant_repo):
        self.tenant_repo = tenant_repo

    def list_tenants(self, user_id: str) -> TenantListResponse:
        try:
            # Call the method that returns a list!
            tenants = self.tenant_repo.get_all_by_owner_id(user_id)
            return TenantListResponse(
                tenants=[TenantSummary.model_validate(t) for t in tenants],
                total=len(tenants),
            )
        except Exception as e:
            logger.error(f"Failed to list tenants for user {user_id}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch tenants.")
