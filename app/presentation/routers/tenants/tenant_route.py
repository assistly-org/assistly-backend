from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.presentation.schemas.tenant import TenantCreateRequest, TenantCreateResponse
from app.presentation.dependencies.current_user import get_current_user
from app.presentation.dependencies.tenant_deps import get_tenant_setup_service
from app.domain.exceptions import SubdomainTakenError
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db
from app.presentation.dependencies.permissions.permissions import is_workspace_owner
# ⚡ 1. Import your Bouncer!
from app.presentation.dependencies.permissions.permissions import is_workspace_owner
from app.presentation.dependencies.tenant_deps import get_delete_tenant_service

router = APIRouter(prefix="/tenant", tags=["Tenants"])


@router.get("/settings")
def get_workspace_settings(
    auth_context: dict = Depends(is_workspace_owner)
):
    return {
        "message": "Welcome to your workspace settings!",
        "security_context": auth_context
    }

@router.get("/my-tenant-info")
def get_tenant_info(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(is_workspace_owner),
):
    """
    If the code reaches this line, the Bouncer has already guaranteed:
    1. They have a valid JWT.
    2. They have the 'tenant_admin' role.
    3. Their token's tenant_subdomain perfectly matches the URL they are hitting.
    """

    # Pro-tip: Use getattr() just in case the middleware failed to set it,
    # so your app doesn't crash with an AttributeError!
    current_subdomain = getattr(request.state, "subdomain", None)
    current_schema_name = getattr(request.state, "schema_name", None)

    return {
        "message": "You are currently inside your securely protected workspace.",
        "active_subdomain": current_subdomain,
        "active_schema_name": current_schema_name,
        "user_id": current_user_id,  # ⚡ You also get the user's ID for free from the Bouncer!
    }

#==============================================================
#========================================================



# For creating orgnisation to work
@router.post("/create", response_model=TenantCreateResponse)
def create_workspace(
    request: TenantCreateRequest,
    current_user=Depends(get_current_user),
    service=Depends(get_tenant_setup_service)
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


@router.delete("/{tenant_id}", status_code=status.HTTP_200_OK)
def delete_workspace(
    tenant_id: str,
    current_user=Depends(get_current_user),
    service=Depends(get_delete_tenant_service)
):
    try:
        # Execute the service with the ID from the URL and the ID of the logged-in user
        service.execute(tenant_id=tenant_id, current_user_id=current_user.id)

        return {
            "status": "success",
            "message": "Organization and workspace deleted successfully"
        }

    except ValueError as e:
        # Raised if tenant is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        # Raised if someone else tries to delete it
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        # Catch-all for database drops or schema errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the organization."
        )


