# app/presentation/routers/auth.py
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db
from app.presentation.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.presentation.dependencies.auth_deps import get_register_service, get_verify_service
from app.domain.exceptions import ValidationError, UserAlreadyExistsError, SubdomainTakenError
from app.domain.exceptions import RegistrationExpiredError, InvalidOTPError


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, service=Depends(get_register_service)):
    try:
        return service.register(data=request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserAlreadyExistsError as e:
        # You can inspect the error message if you want to differentiate 400 vs 409
        status_code = 400 if "unverified" in str(e) else 409
        raise HTTPException(status_code=status_code, detail=str(e))
    except SubdomainTakenError as e:
        raise HTTPException(status_code=409, detail=str(e))




@router.post("/verify", response_model=VerifyResponse)
def verify(
    request: VerifyRequest,
    response: Response,
    db: Session = Depends(get_db), # ⚡ Keep this here to manage the transaction
    service=Depends(get_verify_service),
):
    try:
        # 1. Call the service (Notice we no longer pass db=db!)
        result = service.verify_otp(data=request)
        
        # 2. Transaction Boundary: Commit the DB ONLY if the service succeeds
        db.commit()

        # 3. Set the HTTP-Only Cookie
        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            secure=False, # Set to True in production!
            samesite="lax",
            max_age=604800,
        )
        
        return result

    # 4. Handle specific Domain Errors and turn them into HTTP Errors
    except RegistrationExpiredError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
        
    except InvalidOTPError as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e))
        
    except Exception as e:
        db.rollback()
        # Log the real error here in production
        raise HTTPException(status_code=500, detail="Workspace setup failed. Please try again.")