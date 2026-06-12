# app/application/use_cases/auth/google_auth.py
import json
import uuid
import logging
from fastapi import HTTPException
from app.domain.entities.user import User
from app.domain.entities.tenant import Tenant
from app.presentation.schemas.auth import (
    GoogleAuthRequest,
    GoogleAuthResponse,
    GoogleSetupRequest,
    GoogleSetupResponse,
)

logger = logging.getLogger("assistly")


class GoogleAuthService:
    def __init__(
        self,
        user_repo,
        tenant_repo,
        google_service,
        cache_service,
        token_service,
        task_dispatcher,
    ):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo
        self.google_service = google_service
        self.cache_service = cache_service
        self.token_service = token_service
        self.task_dispatcher = task_dispatcher

    def google_login(self, data: GoogleAuthRequest) -> GoogleAuthResponse:
        # --- VERIFY GOOGLE TOKEN ---
        google_data = self.google_service.verify_google_token(data.id_token)
        if not google_data:
            raise HTTPException(status_code=401, detail="Invalid Google token")

        # --- CHECK IF USER EXISTS ---
        user = self.user_repo.get_by_email(google_data["email"])
        if user:
            # Existing user — just return tokens
            tenant = self.tenant_repo.get_by_owner_id(user.id)
            token_payload = {
                "sub": str(user.id),
                "email": user.email,
                "tenant_slug": tenant.slug,
            }
            logger.info(f"Google login successful for {user.email}")
            return GoogleAuthResponse(
                requires_setup=False,
                access_token=self.token_service.create_access_token(token_payload),
                refresh_token=self.token_service.create_refresh_token(
                    {"sub": str(user.id)}
                ),
                message="Login successful.",
            )

        # --- NEW USER — store in Redis, ask for setup ---
        setup_token = str(uuid.uuid4())
        payload = json.dumps(
            {
                "email": google_data["email"],
                "name": google_data["name"],
                "picture": google_data["picture"],
                "google_id": google_data["google_id"],
            }
        )
        self.cache_service.set(f"google_setup:{setup_token}", 600, payload)

        logger.info(f"New Google user {google_data['email']} — setup required.")
        return GoogleAuthResponse(
            requires_setup=True,
            setup_token=setup_token,
            message="Please complete your workspace setup.",
        )

    def google_setup(self, data: GoogleSetupRequest, db) -> GoogleSetupResponse:
        # --- FETCH FROM REDIS ---
        raw = self.cache_service.get(f"google_setup:{data.setup_token}")
        if not raw:
            raise HTTPException(
                status_code=400, detail="Setup token expired or invalid."
            )

        payload = json.loads(raw)

        # --- CHECK SUBDOMAIN ---
        if self.tenant_repo.get_by_slug(data.subdomain):
            raise HTTPException(status_code=409, detail="Subdomain already taken")

        try:
            # --- CREATE USER ---
            new_user = User(
                email=payload["email"],
                password_hash="",
                auth_provider="google",
                is_active=True,
            )
            new_user = self.user_repo.create_user(new_user)

            # --- CREATE TENANT ---
            new_tenant = Tenant(
                name=data.company_name,
                slug=data.subdomain,
                owner_id=new_user.id,
                created_by=new_user.id,
            )
            self.tenant_repo.create_tenant(new_tenant)

            # --- COMMIT ---
            db.commit()

            # --- DISPATCH TENANT TASK ---

            self.task_dispatcher.dispatch_tenant_creation(new_tenant.slug)

            # --- CLEANUP REDIS ---
            self.cache_service.delete(f"google_setup:{data.setup_token}")

            token_payload = {
                "sub": str(new_user.id),
                "email": new_user.email,
                "tenant_slug": new_tenant.slug,
            }

            logger.info(
                f"Google setup complete for {new_user.email}. Tenant task queued."
            )
            return GoogleSetupResponse(
                access_token=self.token_service.create_access_token(token_payload),
                refresh_token=self.token_service.create_refresh_token(
                    {"sub": str(new_user.id)}
                ),
                message="Welcome to your workspace! Your environment is being prepared.",
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Google setup failed for {payload['email']}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Workspace setup failed. Please try again."
            )
