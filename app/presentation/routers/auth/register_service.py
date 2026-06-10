# app/presentation/routers/auth.py
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db

from app.presentation.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    VerifyRequest,
    VerifyResponse,
)

# Assuming you added get_verify_service to your dependencies.py
from app.presentation.dependencies import get_register_service, get_verify_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, service=Depends(get_register_service)):
    return service.register(data=request)


@router.post("/verify", response_model=VerifyResponse)
def verify(
    request: VerifyRequest,
    response: Response,  # <-- Inject the FastAPI Response object
    db: Session = Depends(get_db),
    service=Depends(get_verify_service),
):
    result = service.verify_otp(data=request, db=db)
    
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,  # Your service still provides this property
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=604800,  # 7 days
    )
    return result
