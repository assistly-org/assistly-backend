from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
# ⚡ 1. IMPORT THE JOSE EXCEPTIONS
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from app.infrastructure.auth.jwt_services import JwtService
from app.infrastructure.db.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository

security = HTTPBearer()

def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = auth.credentials

    try:
        payload = JwtService.decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is empty.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing the user ID.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # ⚡ 3. CATCH THE EXPIRATION AND RETURN A CLEAN 401
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

    # --- 4. FETCH THE USER (Your existing logic) ---
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive."
        )
        
    return user