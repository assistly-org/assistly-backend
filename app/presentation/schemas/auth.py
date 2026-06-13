# app/presentation/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Dict

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
    message : str
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