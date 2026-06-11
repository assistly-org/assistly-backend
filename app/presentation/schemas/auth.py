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