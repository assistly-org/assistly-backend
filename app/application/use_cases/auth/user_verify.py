import json
import logging
from app.domain.entities.user import User
from app.presentation.schemas.auth import VerifyRequest, VerifyResponse
from app.domain.exceptions import RegistrationExpiredError, InvalidOTPError
from sqlalchemy.orm import Session

logger = logging.getLogger("assistly")

class VerifyService:
    def __init__(
        self,
        db: Session,
        user_repo,
        cache_service,
        token_service
        # ⚡ Removed tenant_repo and task_dispatcher
    ):
        self.db = db
        self.user_repo = user_repo
        self.cache_service = cache_service
        self.token_service = token_service

    def verify_otp(self, data: VerifyRequest): # -> VerifyResponse
        # --- FETCH PENDING REGISTRATION ---
        raw = self.cache_service.get(f"registration:{data.email}")
        if not raw:
            logger.warning(f"No pending registration found for {data.email}")
            raise RegistrationExpiredError("OTP has expired or registration was never initiated.")

        payload = json.loads(raw)

        # --- VALIDATE OTP ---
        if payload["otp"] != data.otp_code:
            logger.warning(f"Incorrect OTP entered for {data.email}")
            raise InvalidOTPError("Invalid OTP code")

        # --- ALL OR NOTHING TRANSACTION ---
        try:
            # 1. Create Global User
            new_user = User(
                email=payload["email"],
                password_hash=payload["password_hash"],
                name=payload.get("name"),   # Restore name from cache
                phone=payload.get("phone"), # Restore phone from cache
                is_active=True,
                is_verified=True,           # ⚡ Mark them as officially verified
                auth_provider="local"
            )
            new_user = self.user_repo.create_user(new_user)

            # 2. Delete Redis key so OTP can't be reused
            self.cache_service.delete(f"registration:{data.email}")

            # 3. COMMIT THE TRANSACTION
            self.db.commit()

            # 4. Generate Initial Global Tokens (No Tenant Attached)
            token_payload = {
                "sub": str(new_user.id),
                "email": new_user.email
            }

            logger.info(f"User {data.email} verified successfully. Awaiting workspace setup.")

            return {
                "message": "Account verified successfully. Please set up your workspace.",
                "access_token": self.token_service.create_access_token(data=token_payload),
                "refresh_token": self.token_service.create_refresh_token(data={"sub": str(new_user.id)}),
                "token_type": "bearer",
                "requires_workspace_setup": True, 
                "user": {
                    "id": str(new_user.id),
                    "email": new_user.email,
                    "name": new_user.name
                }
            }

        except Exception as e:
            # ROLLBACK IF DB FAILS
            self.db.rollback()
            logger.error(f"Verification pipeline crashed for {data.email}", exc_info=True)
            raise Exception("Account creation failed. Please try again.")