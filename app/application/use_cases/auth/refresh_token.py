import logging
from app.domain.exceptions import InvalidTokenError, UserNotFoundError

logger = logging.getLogger("assistly")

class RefreshTokenService:
    def __init__(
        self, 
        user_repo, 
        tenant_repo,  
        token_service,
        cache_service 
    ):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo 
        self.token_service = token_service
        self.cache_service = cache_service

    def execute(self, refresh_token: str) -> dict:
        if not refresh_token:
            logger.warning("Refresh attempt failed: No token provided.")
            raise InvalidTokenError("Refresh token missing.")

        # 1. CHECK THE BLACKLIST FIRST
        is_blacklisted = self.cache_service.get(f"blacklist:{refresh_token}")
        if is_blacklisted:
            logger.critical("🚨 SECURITY ALERT: Attempted reuse of a blacklisted refresh token!")
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

        # ⚡ 5. FETCH TENANT
        # Reach into the DB to find the workspace they own, exactly like Login
        tenant = self.tenant_repo.get_by_owner_id(user.id)
        tenant_slug = tenant.slug if tenant else None

        # 6. BLACKLIST THE CURRENT TOKEN
        self.cache_service.set(f"blacklist:{refresh_token}", 604800, "revoked")

        # 7. Forge the brand new tokens
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "tenant_slug": tenant_slug 
        }
        
        new_access_token = self.token_service.create_access_token(data=token_payload)
        new_refresh_token = self.token_service.create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"🔄 Tokens rotated and refreshed successfully for user: {user.email}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token, 
            "token_type": "bearer"
        }