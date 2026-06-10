# app/presentation/schemas/auth.py
from pydantic import BaseModel, EmailStr

# --- REGISTRATION ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    subdomain: str

class RegisterResponse(BaseModel):
    message: str
    # Notice: No tokens here anymore! Just a success message.

# --- VERIFICATION ---
class VerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str

class VerifyResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"