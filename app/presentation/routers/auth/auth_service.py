# app/presentation/routers/auth.py

from fastapi import APIRouter, Depends, Response, HTTPException, status, Cookie
from sqlalchemy.orm import Session

from app.infrastructure.db.database import get_db
from app.presentation.schemas.auth import (
    RegisterRequest, RegisterResponse,
    VerifyRequest, VerifyResponse,
    LoginRequest, LoginResponse, TokenRefreshResponse,
    VerifyForgotPasswordRequest,
    VerifyForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from app.presentation.dependencies.auth_deps import (
    get_register_service,
    get_verify_forgot_password_service,
    get_verify_service,
    get_login_service,
    get_refresh_service,
    get_logout_service,
    get_forgot_password_service,
    get_verify_forgot_password_service,
    get_reset_password_service,
    get_change_password_service

)
from app.domain.exceptions import (
    ValidationError,
    UserAlreadyExistsError,
    SubdomainTakenError,
    RegistrationExpiredError,
    InvalidOTPError,
    InvalidCredentialsError,
    AccountDisabledError,
    InvalidTokenError,
    UserNotFoundError
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, service=Depends(get_register_service)):
    try:
        return service.register(data=request)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserAlreadyExistsError as e:
        status_code = status.HTTP_400_BAD_REQUEST if "unverified" in str(
            e) else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=str(e))
    except SubdomainTakenError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/verify", response_model=VerifyResponse)
def verify(
    request: VerifyRequest,
    response: Response,
    db: Session = Depends(get_db),
    service=Depends(get_verify_service),
):
    try:
        # 1. result is now a dictionary
        result = service.verify_otp(data=request)

        db.commit()

        # 2. ⚡ Use bracket notation here!
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=604800,
        )

        # 3. FastAPI will strip the refresh_token based on VerifyResponse
        return result

    except RegistrationExpiredError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidOTPError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Workspace setup failed. Please try again.")


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    response: Response,
    service=Depends(get_login_service)
):
    try:
        # 1. result is now a raw dictionary containing both tokens
        result = service.login(request)

        # 2. Grab the refresh token from the dictionary and set the cookie
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],  # ⚡ Use bracket notation!
            httponly=True,
            secure=False,  # Set to True in production!
            samesite="lax",
            max_age=604800,
        )

        # 3. Return the dictionary.
        # ⚡ FastAPI's response_model will automatically strip out the "refresh_token"
        # so it NEVER shows up in the JSON response to the user!
        return result

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


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(
    response: Response,  # ⚡ Inject Response to handle the new cookie
    refresh_token: str | None = Cookie(None),
    service=Depends(get_refresh_service)
):
    try:
        # 1. Execute the rotation
        result = service.execute(refresh_token=refresh_token)

        # ⚡ 2. Overwrite the old cookie with the brand new refresh token!
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=False,  # Set to True in production!
            samesite="lax",
            max_age=604800,
        )

        # 3. Return the new access token to the client
        # (We don't need to return the refresh_token in the JSON body since it's in the cookie)
        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not refresh token.")


@router.post("/logout")
def logout(
    response: Response,
    # ⚡ Grab the token directly from the hidden cookie
    refresh_token: str | None = Cookie(None),
    service=Depends(get_logout_service)
):
    # 1. Send the token to the Use Case to be blacklisted in Redis
    service.execute(refresh_token=refresh_token)

    # 2. Instruct the user's browser to physically delete the cookie
    response.delete_cookie(
        key="refresh_token",
        secure=False,  # Set to True in production!
        httponly=True,
        samesite="lax"
    )

    return {"message": "Successfully logged out. Session revoked securely."}

#------- FORGOT PASSWORD ROUTES -------#

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse
)
def forgot_password(
    request: ForgotPasswordRequest,
    service=Depends(get_forgot_password_service)
):
    return service.execute(request)

@router.post(
    "/verify-forgot-password",
    response_model=VerifyForgotPasswordResponse
)
def verify_forgot_password(
    request: VerifyForgotPasswordRequest,
    service=Depends(get_verify_forgot_password_service)
):
    return service.execute(request)

@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    service=Depends(get_reset_password_service)
):
    try:
        result = service.execute(request)

        db.commit()

        return result

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
#-------- change password route ---------#

from app.presentation.dependencies.current_user import get_current_user

@router.get("/me")
def me(
    current_user=Depends(get_current_user)
):
    return current_user

@router.post(
    "/change-password",
    response_model=ChangePasswordResponse
)
def change_password(
    request: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    service=Depends(get_change_password_service)
):
    return service.execute(
        current_user,
        request
    )