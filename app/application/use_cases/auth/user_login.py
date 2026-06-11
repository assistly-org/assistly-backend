# app/application/use_cases/auth/user_login.py

import logging
from app.presentation.schemas.auth import LoginRequest, LoginResponse
from app.domain.exceptions import InvalidCredentialsError, AccountDisabledError

logger = logging.getLogger("assistly")

class LoginService:
    def __init__(
        self,
        user_repo,
        tenant_repo,  # ⚡ 1. Inject the tenant repository here
        hash_service,
        token_service
    ):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo  # ⚡ 2. Assign it to self
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
        if not user.is_active:
            logger.warning(f"Failed login: Account inactive/unverified for {data.email}")
            raise AccountDisabledError("Account is unverified. Please verify your OTP.")

        # ⚡ 4. FETCH TENANT
        # Reach into the DB to find the workspace they own
        tenant = self.tenant_repo.get_by_owner_id(user.id)
        tenant_slug = tenant.slug if tenant else None

        # --- 5. GENERATE TOKENS ---
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "tenant_slug": tenant_slug  # ⚡ 6. Add it to the JWT payload!
        }

        access_token = self.token_service.create_access_token(data=token_payload)
        refresh_token = self.token_service.create_refresh_token(data={"sub": str(user.id)})

        logger.info(f"✅ User {data.email} successfully authenticated.")

        return {
            "message": "login successfully and authenticated.",
            "access_token": access_token,
            "refresh_token": refresh_token, 
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "tenant_slug": tenant_slug # ⚡ Adding it to the visual response is highly recommended too!
            }
        }