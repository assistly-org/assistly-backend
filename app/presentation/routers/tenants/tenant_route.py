from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db 

# ⚡ 1. Import your Bouncer!
from app.presentation.dependencies.permissions.permissions import is_tenant_admin

router = APIRouter()

router = APIRouter(prefix="/tenant", tags=["Tenants"])


@router.get("/my-tenant-info")
def get_tenant_info(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(is_tenant_admin) 
):
    """
    If the code reaches this line, the Bouncer has already guaranteed:
    1. They have a valid JWT.
    2. They have the 'tenant_admin' role.
    3. Their token's tenant_slug perfectly matches the URL they are hitting.
    """
    
    # Pro-tip: Use getattr() just in case the middleware failed to set it, 
    # so your app doesn't crash with an AttributeError!
    current_subdomain = getattr(request.state, "subdomain", None) 
    current_schema_name = getattr(request.state, "schema_name", None)
    
    return {
        "message": "You are currently inside your securely protected workspace.",
        "active_subdomain": current_subdomain, 
        "active_schema_name": current_schema_name,
        "user_id": current_user_id # ⚡ You also get the user's ID for free from the Bouncer!
    }