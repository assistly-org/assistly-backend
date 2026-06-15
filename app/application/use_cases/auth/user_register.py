import random
import json
import logging
import re

from app.presentation.schemas.auth import RegisterRequest, RegisterResponse
from app.domain.exceptions import ValidationError
from app.domain.exceptions import UserAlreadyExistsError, SubdomainTakenError

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

def validate_subdomain(subdomain: str) -> None:
    # 1. Check basic length and characters (lowercase, numbers, and hyphens only)
    # Cannot start or end with a hyphen.
    if not re.match(r"^[a-z0-9](?:[a-z0-9\-]{1,61}[a-z0-9])?$", subdomain):
        raise ValidationError(
            "Subdomain must be 3-63 characters, use only lowercase letters, numbers, or hyphens, and cannot start/end with a hyphen."
        )
    
    # 2. Block reserved system subdomains so users can't hijack your API!
    reserved_subdomains = {"www", "api", "admin", "mail", "public", "support", "app", "tenant_template"}
    if subdomain in reserved_subdomains:
        raise ValidationError("This subdomain is reserved and cannot be registered.")

def validate_company_name(name: str) -> None:
    if not name or len(name.strip()) < 2:
        raise ValidationError("Company name must be at least 2 characters long")
    if len(name) > 100:
        raise ValidationError("Company name is too long (maximum 100 characters)")


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
        validate_subdomain(data.subdomain)   # ⚡ New Subdomain Protection!
        validate_company_name(data.company_name) # ⚡ New Company Name Protection!
        
        user = self.user_repo.get_by_email(data.email)

        if user:
            if not user.is_active:
                logger.warning(f"Unverified account re-registration attempt: {data.email}")
                raise UserAlreadyExistsError("Account exists but is unverified. Please request a new OTP.")
            raise UserAlreadyExistsError("Email already registered")

        if self.tenant_repo.get_by_slug(data.subdomain):
            raise SubdomainTakenError("Subdomain already taken")

        # --- PREPARE PAYLOAD ---
        hashed_password = self.hash_service.hash_password(data.password)
        otp_code = str(random.randint(100000, 999999))
        logger.info(f"otp code {otp_code} 🔑 OTP dispatched.")

        payload = json.dumps({
            "email": data.email,
            "password_hash": hashed_password,
            "company_name": data.company_name,
            "subdomain": data.subdomain,
            "otp": otp_code,
        })

        # --- STORE IN REDIS ---
        self.cache_service.set(f"registration:{data.email}", 300, payload)

        # --- DISPATCH OTP EMAIL VIA INTERFACE ---
        self.task_dispatcher.dispatch_otp_email(data.email, otp_code)

        logger.info(f"Registration payload cached for {data.email}. OTP dispatched.")
        return RegisterResponse(message="Please check your email for the OTP.")