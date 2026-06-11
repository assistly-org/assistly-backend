# app/application/use_cases/auth/refresh_token.py

import logging
from app.domain.exceptions import InvalidTokenError, UserNotFoundError

logger = logging.getLogger("assistly")

class RefreshTokenService:
    def __init__(
        self, 
        user_repo, 
        token_service,
        cache_service # ⚡ Inject Redis here to handle the blacklist!
    ):
        self.user_repo = user_repo
        self.token_service = token_service
        self.cache_service = cache_service

    def execute(self, refresh_token: str) -> dict:
        if not refresh_token:
            logger.warning("Refresh attempt failed: No token provided.")
            raise InvalidTokenError("Refresh token missing.")

        # ⚡ 1. CHECK THE BLACKLIST FIRST
        is_blacklisted = self.cache_service.get(f"blacklist:{refresh_token}")
        if is_blacklisted:
            logger.critical("🚨 SECURITY ALERT: Attempted reuse of a blacklisted refresh token!")
            # In a mega-strict system, you would ban the user here. For now, just block it.
            raise InvalidTokenError("This token has been revoked. Please log in again.")

        # 2. Decode and verify the token type
        payload = self.token_service.decode_token(refresh_token)
        if not payload or payload.get("token_type") != "refresh":
            logger.warning("Refresh attempt failed: Invalid token type.")
            raise InvalidTokenError("Invalid refresh token.")

        # 3. Fetch the user
        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(user_id) 
        
        # 4. Security Check
        if not user or not user.is_active:
            logger.warning(f"Refresh failed: User {user_id} inactive or deleted.")
            raise UserNotFoundError("User account is inactive or not found.")

        # ⚡ 5. BLACKLIST THE CURRENT TOKEN
        # Store it in Redis for 7 days (604800 seconds) so it can never be used again.
        self.cache_service.set(f"blacklist:{refresh_token}", 604800, "revoked")

        # 6. Forge the brand new tokens
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
        
        new_access_token = self.token_service.create_access_token(data=token_payload)
        
        # ⚡ Generate a brand new refresh token!
        new_refresh_token = self.token_service.create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"🔄 Tokens rotated and refreshed successfully for user: {user.email}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token, # Send this back to the router!
            "token_type": "bearer"
        }