import random
import json
import logging
import re

from app.presentation.schemas.auth import RegisterRequest, RegisterResponse
from app.domain.exceptions import ValidationError
from app.domain.exceptions import UserAlreadyExistsError

logger = logging.getLogger("assistly")

# --- BULLETPROOF VALIDATORS ---

def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number")

def validate_email(email: str) -> None:
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise ValidationError("Invalid email address")



class RegisterService:
    def __init__(
        self, 
        user_repo, 
        tenant_repo, 
        hash_service, 
        email_service, 
        cache_service,
        task_dispatcher 
    ):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo
        self.hash_service = hash_service
        self.email_service = email_service
        self.cache_service = cache_service
        self.task_dispatcher = task_dispatcher

    def register(self, data: RegisterRequest) -> RegisterResponse:
        # --- PRE-FLIGHT CHECKS & VALIDATION ---
        validate_password(data.password) 
        validate_email(data.email)       
       
        
        user = self.user_repo.get_by_email(data.email)

        if user:
            if not user.is_active:
                logger.warning(f"Unverified account re-registration attempt: {data.email}")
                raise UserAlreadyExistsError("Account exists but is unverified. Please request a new OTP.")
            raise UserAlreadyExistsError("Email already registered")


        # --- PREPARE PAYLOAD ---
        hashed_password = self.hash_service.hash_password(data.password)
        otp_code = str(random.randint(100000, 999999))
        logger.info(f"otp code {otp_code} 🔑 OTP dispatched.")

        payload = json.dumps({
            "email": data.email,
            "password_hash": hashed_password,
            "name": data.name,
            "phone": data.phone,
            "otp": otp_code,
        })

        # --- STORE IN REDIS ---
        self.cache_service.set(f"registration:{data.email}", 300, payload)

        # --- DISPATCH OTP EMAIL VIA INTERFACE ---
        self.task_dispatcher.dispatch_otp_email(data.email, otp_code)

        logger.info(f"Registration payload cached for {data.email}. OTP dispatched.")
        return RegisterResponse(message="Please check your email for the OTP.")