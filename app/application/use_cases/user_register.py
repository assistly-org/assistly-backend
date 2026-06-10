# app/application/use_cases/user_register.py
import random
import traceback
from fastapi import HTTPException, status
from app.infrastructure.models.auth.users import User
from app.infrastructure.models.auth.tenants import Tenant
from app.presentation.schemas.auth import RegisterRequest, RegisterResponse
from app.infrastructure.cache.redis_client import redis_db

from app.infrastructure.email.tasks import send_otp_email_task

import logging

logger = logging.getLogger("assistly")


class RegisterService:
    def __init__(self, user_repo, tenant_repo, hash_service, email_service):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo
        self.hash_service = hash_service
        self.email_service = email_service  

    def register(self, data: RegisterRequest, db) -> RegisterResponse:
        # --- PRE-FLIGHT CHECKS ---
        user = self.user_repo.get_by_email(data.email)
        if user:
            # EDGE CASE FIX: What if they registered but the OTP expired?
            if not user.is_active:
                logger.warning(
                    f"Registration attempt by unverified existing user: {data.email}"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Account exists but is unverified. Please request a new OTP.",
                )
            raise HTTPException(status_code=409, detail="Email already registered")

        if self.tenant_repo.get_by_slug(data.subdomain):
            raise HTTPException(status_code=409, detail="Subdomain already taken")

        hashed_password = self.hash_service.hash_password(data.password)
        otp_code = str(random.randint(100000, 999999))
        print(f"otp is here {otp_code}")

        # --- THE "ALL OR NOTHING" TRANSACTION ---
        try:
            # 1. Stage User
            new_user = User(
                email=data.email, password_hash=hashed_password, is_active=False
            )
            new_user = self.user_repo.create_user(new_user)

            # 2. Stage Tenant
            new_tenant = Tenant(
                name=data.company_name,
                slug=data.subdomain,
                owner_id=new_user.id,
                created_by=new_user.id,
            )
            self.tenant_repo.create_tenant(new_tenant)

            # 3. Stage Redis (Do this BEFORE db.commit)
            # If Redis is offline, this crashes and triggers db.rollback() automatically!
            redis_db.setex(f"otp:{data.email}", 300, otp_code)

            # 4. Make it permanent
            db.commit()

            # self.email_service.send_otp(to_email=data.email, otp_code=otp_code)
            send_otp_email_task.delay(data.email, otp_code)

            logger.info(
                f"Registration successful for {data.email}. OTP dispatched to Celery background thread."
            )
            return RegisterResponse(message="Please check your email for the OTP.")

        except Exception as e:
            # If ANYTHING above fails, wipe it all.
            db.rollback()
            logger.error(
                f"Registration failed for user {data.email} due to system exception.",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail="Registration failed due to a system error."
            )
