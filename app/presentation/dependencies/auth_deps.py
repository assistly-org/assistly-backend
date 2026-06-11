# app/presentation/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.infrastructure.auth.bcrypt_hash_service import BcryptHashService
from app.application.use_cases.auth.user_register import RegisterService
from app.application.use_cases.auth.user_verify import VerifyService
from app.infrastructure.worker.email.smtp_services import EmailService
from app.infrastructure.cache.redis_service import RedisService
from app.infrastructure.auth.jwt_services import JwtService

# ⚡ Import your new dispatcher
from app.infrastructure.worker.celery_dispatcher import CeleryTaskDispatcher


def get_verify_service(db: Session = Depends(get_db)) -> VerifyService:
    user_repo = UserRepository(db)
    tenant_repo = TenantRepository(db)
    cache_service = RedisService()
    token_service = JwtService()
    
    # ⚡ Initialize the dispatcher
    task_dispatcher = CeleryTaskDispatcher()

    return VerifyService(
        user_repo=user_repo,
        tenant_repo=tenant_repo,
        cache_service=cache_service,
        token_service=token_service,
        task_dispatcher=task_dispatcher, 
    )


def get_register_service(db: Session = Depends(get_db)) -> RegisterService:
    """
    Builds and returns a fully initialized RegisterService.
    FastAPI will automatically run this whenever a route requests it.
    """
    # 1. Provide the DB session to the Repositories
    user_repo = UserRepository(db)      
    tenant_repo = TenantRepository(db)  
    email_service = EmailService()

    # 2. Initialize the Hash Service and Cache
    hash_service = BcryptHashService()
    cache_service = RedisService()
    
    # ⚡ 3. Initialize the dispatcher (ADD THIS LINE)
    task_dispatcher = CeleryTaskDispatcher()

    # 4. Inject all dependencies into the Service
    return RegisterService(
        user_repo=user_repo,
        tenant_repo=tenant_repo,
        hash_service=hash_service,
        email_service=email_service,
        cache_service=cache_service,  
        task_dispatcher=task_dispatcher, # ⚡ ADD THIS LINE to fix the TypeError!
    )