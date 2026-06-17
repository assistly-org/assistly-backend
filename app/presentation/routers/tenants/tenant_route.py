from fastapi import APIRouter, Depends, HTTPException, status
from app.presentation.schemas.tenant import TenantCreateRequest, TenantCreateResponse
from app.presentation.dependencies.current_user import get_current_user
from app.presentation.dependencies.tenant_deps import get_tenant_setup_service
from app.domain.exceptions import SubdomainTakenError
# ⚡ 1. Import your Bouncer!
from app.presentation.dependencies.permissions.permissions import is_workspace_owner

router = APIRouter()

router = APIRouter(prefix="/tenant", tags=["Tenants"])

@router.get("/settings")
def get_workspace_settings(
    auth_context: dict = Depends(is_workspace_owner) 
):
    return {
        "message": "Welcome to your workspace settings!",
        "security_context": auth_context
    }


# For creating orgnisation to work
@router.post("/create", response_model=TenantCreateResponse)
def create_workspace(
    request: TenantCreateRequest,
    current_user = Depends(get_current_user),
    service = Depends(get_tenant_setup_service)
):
    try:
        return service.execute(current_user=current_user, data=request)
        
    except SubdomainTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )