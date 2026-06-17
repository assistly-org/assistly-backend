# app/presentation/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional

class UserResponseObj(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    tenant_slug: Optional[str] = None



# --- REGISTRATION ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name:str
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
    requires_workspace_setup: bool         # Added missing field
    user: UserResponseObj                  # Use the new flexible object


# --- LOGIN ---
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    requires_workspace_setup: bool         # Added missing field
    user: UserResponseObj                  # Use the new flexible object


# --- TOKEN REFRESH ---
class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    
    
#------- FORGOT PASSWORD -------#

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
    
    
#--------change password ---------#

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    message: str
    
    
#------- edit profile -------#

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
class RequestEmailChangeRequest(BaseModel):
    new_email: EmailStr


class RequestEmailChangeResponse(BaseModel):
    message: str


class VerifyEmailChangeRequest(BaseModel):
    new_email: EmailStr
    otp_code: str


class VerifyEmailChangeResponse(BaseModel):
    message: str


# --- GOOOGLE AUTH ---

# --- GOOGLE AUTH ---
class GoogleAuthRequest(BaseModel):
    id_token: str

class GoogleAuthResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    requires_workspace_setup: bool
    user: UserResponseObj  # ⚡ Use the same flexible object we made earlier!


class GoogleSetupRequest(BaseModel):
    setup_token: str
    subdomain: str
    company_name: str


class GoogleSetupResponse(BaseModel):
    access_token: str
    refresh_token: str
    message: str
