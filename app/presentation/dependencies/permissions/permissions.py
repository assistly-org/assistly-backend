from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# ⚡ Import the specific errors from jose
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from app.infrastructure.auth.jwt_services import JwtService

security = HTTPBearer()

class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)) -> str:
        
        raw_token = auth.credentials 

        try:
            # Decode using your service
            payload = JwtService.decode_token(raw_token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token payload is empty.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            user_id: str = payload.get("sub")
            user_role: str = payload.get("role")
            user_tenant_slug: str = payload.get("tenant_slug")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is missing the user ID subject.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # ⚡ 1. Catch Expired Tokens specifically
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.", # Your frontend looks for this exact string!
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # ⚡ 2. Catch Claims errors (e.g., the token is valid but meant for a different audience)
        except JWTClaimsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token claims are invalid. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # ⚡ 3. Fallback for forged, tampered, or malformed tokens
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature or format.",
                headers={"WWW-Authenticate": "Bearer"},
            )


        # --- 4. Check Role Permission ---
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to perform this action."
            )

        # --- 5. Anti-Tenant Hopping Check ---
        url_subdomain = getattr(request.state, "subdomain", None)
        if url_subdomain and user_tenant_slug != url_subdomain:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Security Alert: Your token belongs to '{user_tenant_slug}', but you are trying to access '{url_subdomain}'."
            )

        return user_id


is_tenant_admin = RequireRole(["tenant_admin"])