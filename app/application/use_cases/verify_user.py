# app/application/use_cases/user_verify.py
import logging
from fastapi import HTTPException
from app.infrastructure.auth.jwt_services import JwtService
from app.presentation.schemas.auth import VerifyRequest, VerifyResponse
from app.infrastructure.cache.redis_client import redis_db
from app.infrastructure.worker.tenant_tasks import tenant_create_task

logger = logging.getLogger("assistly")


class VerifyService:
    def __init__(self, user_repo, tenant_repo):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo

    def verify_otp(self, data: VerifyRequest, db) -> VerifyResponse:
        user = self.user_repo.get_by_email(data.email)
        if not user or user.is_active:
            logger.warning(
                f"Failed verification attempt: User missing or already verified -> {data.email}"
            )
            raise HTTPException(status_code=400, detail="Invalid or already verified")

        stored_otp = redis_db.get(f"otp:{data.email}")
        if not stored_otp:
            logger.warning(
                f"Verification failed: Expired OTP cache entry for {data.email}"
            )
            raise HTTPException(
                status_code=400, detail="OTP has expired. Please request a new one."
            )
            
        if stored_otp != data.otp_code:
            logger.warning(
                f"Verification failed: Incorrect OTP string entered for {data.email}"
            )
            raise HTTPException(status_code=401, detail="Invalid OTP code")

        # --- THE "ALL OR NOTHING" TRANSACTION ---
        try:
            # 1. Stage User update
            user.is_active = True
            self.user_repo.update_user(user)

            # 2. Fetch Tenant context
            tenant = self.tenant_repo.get_by_owner_id(user.id)
            if not tenant:
                raise ValueError("Tenant data missing from system state")

            # 3. Commit to Database FIRST
            # We save the user activation state so the user is marked active right now.
            # This must happen before Celery spins up its own database session.
            db.commit()

            # 4. DISPATCH THE HEAVY LIFTING TO CELERY
            # We pass just the string slug. Celery takes care of migrations in the background!
            tenant_create_task.delay(tenant.slug)

            # 5. Delete OTP to prevent reuse (Only after DB is safe)
            redis_db.delete(f"otp:{data.email}")

            token_payload = {
                "sub": str(user.id),
                "email": user.email,
                "tenant_slug": tenant.slug,
            }

            logger.info(f"User {data.email} verified. Tenant workspace creation task queued via Celery.")

            return VerifyResponse(
                message="Welcome to your workspace! Your environment is being prepared in the background.",
                access_token=JwtService.create_access_token(data=token_payload),
                refresh_token=JwtService.create_refresh_token(
                    data={"sub": str(user.id)}
                ),
            )

        except ValueError as ve:
            db.rollback()
            logger.error(f"Tenant isolation lookup violation: {str(ve)}")
            raise HTTPException(status_code=404, detail=str(ve))

        except Exception as e:
            db.rollback()
            # Automatically grabs and formats the complete traceback using exc_info=True
            logger.error(f"Verification pipeline crashed for user {data.email}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Workspace setup failed. Please try again."
            )