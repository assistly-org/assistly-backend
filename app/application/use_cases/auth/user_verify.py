import json
import logging
from fastapi import HTTPException
from app.domain.entities.user import User
from app.domain.entities.tenant import Tenant
from app.presentation.schemas.auth import VerifyRequest, VerifyResponse

logger = logging.getLogger("assistly")


class VerifyService:
    def __init__(self, user_repo, tenant_repo, cache_service, token_service):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo
        self.cache_service = cache_service
        self.token_service = token_service

    def verify_otp(self, data: VerifyRequest, db) -> VerifyResponse:
        # --- FETCH PENDING REGISTRATION ---
        raw = self.cache_service.get(f"registration:{data.email}")
        if not raw:
            logger.warning(f"No pending registration found for {data.email}")
            raise HTTPException(
                status_code=400,
                detail="OTP has expired or registration was never initiated.",
            )

        payload = json.loads(raw)

        # --- VALIDATE OTP ---
        if payload["otp"] != data.otp_code:
            logger.warning(f"Incorrect OTP entered for {data.email}")
            raise HTTPException(status_code=401, detail="Invalid OTP code")

        # --- ALL OR NOTHING TRANSACTION ---
        try:
            # 1. Create User
            new_user = User(
                email=payload["email"],
                password_hash=payload["password_hash"],
                is_active=True,
            )
            # ⚡ CRITICAL: Ensure your UserRepository maps the generated DB ID back to this domain entity!
            new_user = self.user_repo.create_user(new_user)

            # 2. Create Tenant
            # ⚡ DEFENSIVE EXTRACTION: Guarantee Postgres never receives a null name
            safe_name = payload.get("company_name") or payload.get("subdomain")

            new_tenant = Tenant(
                name=safe_name,
                slug=payload["subdomain"],
                owner_id=new_user.id,      # Now safely populated from the repo
                created_by=new_user.id,
            )
            self.tenant_repo.create_tenant(new_tenant)

            # 3. Commit to DB
            db.commit()

            # 4. Dispatch tenant workspace creation
            from app.infrastructure.worker.tenant_tasks import tenant_create_task
            tenant_create_task.delay(new_tenant.slug)

            # 5. Delete Redis key — prevent reuse
            self.cache_service.delete(f"registration:{data.email}")

            # 6. Generate tokens
            token_payload = {
                "sub": str(new_user.id),
                "email": new_user.email,
                "tenant_slug": new_tenant.slug,
            }

            logger.info(f"User {data.email} verified and logged in. Tenant task queued.")

            return VerifyResponse(
                message="Welcome to your workspace! Your environment is being prepared.",
                access_token=self.token_service.create_access_token(data=token_payload),
                refresh_token=self.token_service.create_refresh_token(
                    data={"sub": str(new_user.id)}
                ),
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Verification pipeline crashed for {data.email}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Workspace setup failed. Please try again."
            )