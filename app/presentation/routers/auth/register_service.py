# app/presentation/routers/auth.py

from fastapi import APIRouter, Depends, Response, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.db.database import get_db
from app.presentation.schemas.auth import (
    RegisterRequest, RegisterResponse,
    VerifyRequest, VerifyResponse,
    LoginRequest, LoginResponse
)
from app.presentation.dependencies.auth_deps import (
    get_register_service, 
    get_verify_service, 
    get_login_service
)
from app.domain.exceptions import (
    ValidationError, 
    UserAlreadyExistsError, 
    SubdomainTakenError,
    RegistrationExpiredError, 
    InvalidOTPError,
    InvalidCredentialsError, 
    AccountDisabledError
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, service = Depends(get_register_service)):
    try:
        return service.register(data=request)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserAlreadyExistsError as e:
        status_code = status.HTTP_400_BAD_REQUEST if "unverified" in str(e) else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=str(e))
    except SubdomainTakenError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/verify", response_model=VerifyResponse)
def verify(
    request: VerifyRequest,
    response: Response,
    db: Session = Depends(get_db), 
    service = Depends(get_verify_service),
):
    try:
        result = service.verify_otp(data=request)
        db.commit()

        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            secure=False, # Set to True in production!
            samesite="lax",
            max_age=604800,
        )
        return result

    except RegistrationExpiredError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidOTPError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Workspace setup failed. Please try again.")


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, service = Depends(get_login_service)):
    try:
        # Firing the Use Case injected by dependencies.py
        return service.login(request)
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AccountDisabledError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )