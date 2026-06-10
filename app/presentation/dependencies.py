# app/presentation/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session

# Import your database session provider (adjust the path if yours is different)
from app.infrastructure.db.database import get_db

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.infrastructure.auth.bcrypt_hash_service import BcryptHashService

# Import your RegisterService (adjust path depending on where you saved it)
from app.application.use_cases.auth.user_register import RegisterService

# Add this import at the top of your file
from app.application.use_cases.auth.user_verify import VerifyService

# ... (your existing get_register_service code) ...
from app.infrastructure.email.smtp_services import EmailService


from app.infrastructure.cache.redis_service import RedisService
from app.infrastructure.auth.jwt_services import JwtService


def get_verify_service(db: Session = Depends(get_db)) -> VerifyService:
    user_repo = UserRepository(db)
    tenant_repo = TenantRepository(db)
    cache_service = RedisService()
    token_service = JwtService()

    return VerifyService(
        user_repo=user_repo,
        tenant_repo=tenant_repo,
        cache_service=cache_service,
        token_service=token_service,
    )


def get_register_service() -> RegisterService:
    """
    Builds and returns a fully initialized RegisterService.
    FastAPI will automatically run this whenever a route requests it.
    """
    # 1. Provide the DB session to the Repositories
    user_repo = UserRepository()
    tenant_repo = TenantRepository()
    email_service = EmailService()  # <-- Initialize it here

    # 2. Initialize the Hash Service
    hash_service = BcryptHashService()
    cache_service = RedisService()  # ADD THIS

    # 3. Inject all dependencies into the Service
    return RegisterService(
        user_repo=user_repo,
        tenant_repo=tenant_repo,
        hash_service=hash_service,
        email_service=email_service,
        ache_service=cache_service,  # ADD THIS
    )
