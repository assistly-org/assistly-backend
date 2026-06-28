import logging

logger = logging.getLogger("assistly")

class LogoutService:
    def __init__(self, cache_service):
        self.cache_service = cache_service

    def execute(self, refresh_token: str | None) -> None:
        # If they don't have a token in their cookie, they are effectively already logged out
        if not refresh_token:
            logger.info("Logout called without a refresh token. Proceeding.")
            return

        # ⚡ BLACKLIST THE TOKEN
        # We lock it in Redis for 7 days (604800 seconds). 
        # If anyone tries to use this exact string in the /refresh route, Redis will block them.
        self.cache_service.set(f"blacklist:{refresh_token}", 604800, "revoked")
        
        logger.info("🔒 Refresh token successfully blacklisted during logout.")