from fastapi import APIRouter, Depends

from app.presentation.schemas.organization import TenantListResponse
from app.application.use_cases.organization.list_tenants import ListTenantsService
from app.presentation.dependencies.tenant_deps import get_list_tenants_service

# ⚡ Import your new Bouncer
# from app.presentation.dependencies.permissions.permissions import is_workspace_owner
from app.presentation.dependencies.current_user import get_current_user


router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/all", response_model=TenantListResponse)
def list_my_tenants(
    # ⚡ The Bouncer checks the token, verifies the role, and hands you the user_id as a string
    user: str = Depends(get_current_user),

    service: ListTenantsService = Depends(get_list_tenants_service),
):
    # Pass the ID straight into your business logic!
    return service.list_tenants(user_id=user.id)
