import json
import logging
from app.domain.entities.user import User
from app.domain.entities.tenant import Tenant
from app.presentation.schemas.auth import VerifyRequest, VerifyResponse
from app.domain.exceptions import RegistrationExpiredError, InvalidOTPError

logger = logging.getLogger("assistly")


class VerifyService:
    def __init__(
        self,
        user_repo,
        tenant_repo,
        cache_service,
        token_service,
        task_dispatcher  # ⚡ Inject the Celery abstractor here
    ):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo
        self.cache_service = cache_service
        self.token_service = token_service
        self.task_dispatcher = task_dispatcher

    def verify_otp(self, data: VerifyRequest) -> VerifyResponse:
        # --- FETCH PENDING REGISTRATION ---
        raw = self.cache_service.get(f"registration:{data.email}")
        if not raw:
            logger.warning(f"No pending registration found for {data.email}")
            raise RegistrationExpiredError(
                "OTP has expired or registration was never initiated.")

        payload = json.loads(raw)

        # --- VALIDATE OTP ---
        if payload["otp"] != data.otp_code:
            logger.warning(f"Incorrect OTP entered for {data.email}")
            raise InvalidOTPError("Invalid OTP code")

        # --- ALL OR NOTHING TRANSACTION ---
        # ⚡ Note: In Clean Architecture, the repositories should handle the session,
        # or you should use a Unit of Work. Assuming user_repo handles the add().
        try:
            # 1. Create User
            new_user = User(
                email=payload["email"],
                password_hash=payload["password_hash"],
                is_active=True,
            )
            new_user = self.user_repo.create_user(new_user)

            # 2. Create Tenant
            safe_name = payload.get("company_name") or payload.get("subdomain")
            new_tenant = Tenant(
                name=safe_name,
                slug=payload["subdomain"],
                owner_id=new_user.id,
                created_by=new_user.id,
            )
            self.tenant_repo.create_tenant(new_tenant)

            # 3. Dispatch tenant workspace creation via Interface
            # ⚡ The service doesn't know this uses Celery!
            self.task_dispatcher.dispatch_tenant_creation(new_tenant.slug)

            # 4. Delete Redis key
            self.cache_service.delete(f"registration:{data.email}")

            # 5. Generate tokens
            token_payload = {
                "sub": str(new_user.id),
                "email": new_user.email,
                "tenant_slug": new_tenant.slug,
            }

            logger.info(f"User {data.email} verified and logged in.")

            return {
                "message": "Welcome to your workspace! Your environment is being prepared.",
                "access_token": self.token_service.create_access_token(data=token_payload),
                "refresh_token": self.token_service.create_refresh_token(data={"sub": str(new_user.id)}),
                "token_type": "bearer",
                "user": {
                    "id": str(new_user.id),
                    "email": new_user.email
                }
            }

        except Exception as e:
            logger.error(
                f"Verification pipeline crashed for {data.email}", exc_info=True)
            # Raise a generic Domain Error that the Router will catch
            raise Exception("Workspace setup failed. Please try again.")
