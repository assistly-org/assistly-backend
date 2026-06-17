import logging
from app.presentation.schemas.auth import LoginRequest
from app.domain.exceptions import InvalidCredentialsError, AccountDisabledError

logger = logging.getLogger("assistly")

class LoginService:
    def __init__(
        self,
        user_repo,
        hash_service,
        token_service
    ):
        self.user_repo = user_repo
        self.hash_service = hash_service
        self.token_service = token_service

    def login(self, data: LoginRequest) -> dict:
        logger.info(f"Login attempt initiated for: {data.email}")

        # --- 1. FETCH USER ---
        user = self.user_repo.get_by_email(data.email)

        if not user:
            logger.warning(f"Failed login: No account found for {data.email}")
            raise InvalidCredentialsError("Invalid email or password")

        # --- 2. VERIFY PASSWORD ---
        if not self.hash_service.verify_password(data.password, user.password_hash):
            logger.warning(f"Failed login: Incorrect password for {data.email}")
            raise InvalidCredentialsError("Invalid email or password")

        # --- 3. CHECK ACCOUNT STATUS ---
        if not user.is_active or not user.is_verified:
            logger.warning(f"Failed login: Account inactive/unverified for {data.email}")
            raise AccountDisabledError("Account is unverified. Please verify your OTP.")

        # ⚡ 4. MULTI-TENANT ROUTING
        # Use the routing slug from the global user profile
        tenant_slug = user.last_active_tenant_slug
        
        # ⚡ 5. GENERATE TOKENS (Match Google Auth Payload)
        token_payload = {
            "sub": str(user.id),
            "email": user.email
        }

        access_token = self.token_service.create_access_token(data=token_payload)
        refresh_token = self.token_service.create_refresh_token(data={"sub": str(user.id)})

        logger.info(f"✅ User {data.email} successfully authenticated.")

        return {
            "message": "Login successful.",
            "access_token": access_token,
            "refresh_token": refresh_token, 
            "token_type": "bearer",
            "requires_workspace_setup": True if not tenant_slug else False, # ⚡ Tell UI what to do!
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name":user.name,
                "tenant_slug": tenant_slug 
            }
        }