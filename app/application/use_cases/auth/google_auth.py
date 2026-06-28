import logging
from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.domain.exceptions import InvalidTokenError
from app.presentation.schemas.auth import GoogleAuthRequest

logger = logging.getLogger("assistly")

class GoogleAuthService:
    def __init__(
        self,
        db: Session,              
        user_repo,
        google_service,
        token_service
    ):
        self.db = db
        self.user_repo = user_repo
        self.google_service = google_service
        self.token_service = token_service

    def google_login(self, data: GoogleAuthRequest) -> dict:
        # --- 1. VERIFY GOOGLE TOKEN ---
        google_data = self.google_service.verify_google_token(data.id_token)
        if not google_data:
            logger.warning("Google login failed: Invalid token")
            raise InvalidTokenError("Invalid Google token provided.")

        email = google_data["email"]
        logger.info(f"Google login attempt for: {email}")

        # --- 2. CHECK IF USER EXISTS ---
        user = self.user_repo.get_by_email(email)

        try:
            # --- 3. CREATE NEW GLOBAL USER (If they don't exist) ---
            if not user:
                logger.info(f"New Google user detected. Creating global profile for {email}")
                user = User(
                    email=email,
                    name=google_data.get("name"),
                    avatar_url=google_data.get("picture"),
                    auth_provider="google",
                    oauth_id=google_data.get("google_id"),
                    is_active=True,
                    is_verified=True, 
                    last_active_tenant_slug=None
                )
                user = self.user_repo.create_user(user)
                self.db.commit()

            # --- 4. MULTI-TENANT ROUTING ---
            tenant_slug = user.last_active_tenant_slug

            # --- 5. GENERATE TOKENS ---
            token_payload = {
                "sub": str(user.id),
                "email": user.email
            }

            access_token = self.token_service.create_access_token(token_payload)
            refresh_token = self.token_service.create_refresh_token({"sub": str(user.id)})

            logger.info(f"✅ Google login successful for {email}.")

            # --- 6. RETURN UNIFIED RESPONSE ---
            return {
                "message": "Login successful.",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "requires_workspace_setup": True if not tenant_slug else False,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "tenant_slug": tenant_slug
                }
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Google authentication pipeline crashed for {email}", exc_info=True)
            raise Exception("Authentication failed. Please try again.")