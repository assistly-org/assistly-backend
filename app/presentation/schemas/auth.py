from pydantic import BaseModel, EmailStr
from typing import Optional

class UserResponseObj(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    tenant_slug: Optional[str] = None

# --- PROFILE GET ---
class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    timezone: str | None = None
    is_active: bool
    is_verified: bool
    last_active_tenant_slug: str | None = None

    class Config:
        from_attributes = True

# --- REGISTRATION ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str

class RegisterResponse(BaseModel):
    message: str

# --- VERIFICATION ---
class VerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str

class VerifyResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    requires_workspace_setup: bool
    user: UserResponseObj

# --- LOGIN ---
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    requires_workspace_setup: bool
    user: UserResponseObj

# --- TOKEN REFRESH ---
class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
# ------- FORGOT PASSWORD -------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

class VerifyForgotPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str

class VerifyForgotPasswordResponse(BaseModel):
    message: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

class ResetPasswordResponse(BaseModel):
    message: str
    
# -------- CHANGE PASSWORD --------
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ChangePasswordResponse(BaseModel):
    message: str
    
# ------- EDIT PROFILE -------
class EditProfileRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    timezone: str | None = None
    
class EditProfileResponse(BaseModel):
    message: str
    name: str | None = None
    email: EmailStr
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    timezone: str | None = None

    class Config:
        from_attributes = True

# -------- EMAIL CHANGE --------
class RequestEmailChangeRequest(BaseModel):
    new_email: EmailStr

class RequestEmailChangeResponse(BaseModel):
    message: str

class VerifyEmailChangeRequest(BaseModel):
    new_email: EmailStr
    otp_code: str

class VerifyEmailChangeResponse(BaseModel):
    message: str

# --- GOOGLE AUTH ---
class GoogleAuthRequest(BaseModel):
    id_token: str

class GoogleAuthResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    requires_workspace_setup: bool
    user: UserResponseObj

class GoogleSetupRequest(BaseModel):
    setup_token: str
    subdomain: str
    company_name: str

class GoogleSetupResponse(BaseModel):
    access_token: str
    refresh_token: str
    message: str