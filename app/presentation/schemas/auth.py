# app/presentation/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional


# --- REGISTRATION ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    subdomain: str


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
    user: Dict[str, str]


# --- LOGIN ---
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, str]


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


# --- GOOOGLE AUTH ---


class GoogleAuthRequest(BaseModel):
    id_token: str


class GoogleAuthResponse(BaseModel):
    requires_setup: bool
    setup_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    message: str


class GoogleSetupRequest(BaseModel):
    setup_token: str
    subdomain: str
    company_name: str


class GoogleSetupResponse(BaseModel):
    access_token: str
    refresh_token: str
    message: str
