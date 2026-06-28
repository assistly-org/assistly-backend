from fastapi import APIRouter, Depends

from app.presentation.schemas.organization import TenantListResponse
from app.application.use_cases.organization.list_tenants import ListTenantsService
from app.presentation.dependencies.tenant_deps import get_list_tenants_service

# ⚡ Import your new Bouncer
from app.presentation.dependencies.permissions.permissions import is_tenant_admin


router = APIRouter(prefix="/users/me", tags=["Organizations"])

@router.get("/organizations", response_model=TenantListResponse)
def list_my_tenants(
    # ⚡ The Bouncer checks the token, verifies the role, and hands you the user_id as a string
    user_id: str = Depends(is_tenant_admin),
        
    service: ListTenantsService = Depends(get_list_tenants_service),
):
    # Pass the ID straight into your business logic!
    return service.list_tenants(user_id=user_id)    