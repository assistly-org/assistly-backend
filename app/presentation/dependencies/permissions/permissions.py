from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from app.infrastructure.auth.jwt_services import JwtService
from app.infrastructure.db.database import get_db

# ⚡ Import your new database models to check live permissions!
from app.infrastructure.models.auth.tenants import Tenant
from app.infrastructure.models.auth.tenant_members import TenantMember

security = HTTPBearer()


class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        request: Request,
        auth: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)  # ⚡ Inject the DB here
    ) -> dict:

        raw_token = auth.credentials

        # --- 1. VERIFY GLOBAL IDENTITY (JWT) ---
        try:
            payload = JwtService.decode_token(raw_token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token payload is empty.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id: str = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is missing the user ID subject.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTClaimsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token claims are invalid. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature or format.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # --- 2. GET WORKSPACE CONTEXT FROM URL ---
        url_subdomain = getattr(request.state, "subdomain", None)
        if not url_subdomain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace context (subdomain) is missing from the request."
            )

        # --- 3. FETCH THE WORKSPACE ---
        tenant = db.query(Tenant).filter(
            Tenant.subdomain == url_subdomain,
            Tenant.is_active == True
        ).first()

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or has been suspended."
            )

        # --- 4. CHECK LIVE MULTI-TENANT PERMISSIONS ---
        membership = db.query(TenantMember).filter(
            TenantMember.user_id == user_id,
            TenantMember.tenant_id == tenant.id,
            TenantMember.is_active == True
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security Alert: You are not a member of this workspace."
            )

        if membership.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to perform this action. Required: {self.allowed_roles}, Yours: {membership.role}"
            )

        # --- 5. RETURN RICH CONTEXT TO THE API ROUTE ---
        return {
            "user_id": user_id,
            "tenant_id": tenant.id,
            "tenant_subdomain": tenant.subdomain,
            "role": membership.role
        }


# ⚡ Usage Examples:
is_workspace_owner = RequireRole(["owner"])
is_workspace_admin = RequireRole(["owner", "admin"])
is_workspace_member = RequireRole(["owner", "admin", "member"])
