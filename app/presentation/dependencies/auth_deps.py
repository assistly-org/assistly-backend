# app/presentation/dependencies/auth_deps.py

from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.infrastructure.auth.bcrypt_hash_service import BcryptHashService
from app.infrastructure.auth.jwt_services import JwtService
from app.infrastructure.worker.email.smtp_services import EmailService
from app.infrastructure.cache.redis_service import RedisService
from app.infrastructure.worker.celery_dispatcher import CeleryTaskDispatcher

from app.application.use_cases.auth.user_register import RegisterService
from app.application.use_cases.auth.user_verify import VerifyService
from app.application.use_cases.auth.user_login import LoginService


def get_verify_service(db: Session = Depends(get_db)) -> VerifyService:
    user_repo = UserRepository(db)
    tenant_repo = TenantRepository(db)
    cache_service = RedisService()
    token_service = JwtService()
    task_dispatcher = CeleryTaskDispatcher()

    return VerifyService(
        user_repo=user_repo,
        tenant_repo=tenant_repo,
        cache_service=cache_service,
        token_service=token_service,
        task_dispatcher=task_dispatcher, 
    )


def get_register_service(db: Session = Depends(get_db)) -> RegisterService:
    user_repo = UserRepository(db)      
    tenant_repo = TenantRepository(db)  
    email_service = EmailService()
    hash_service = BcryptHashService()
    cache_service = RedisService()
    task_dispatcher = CeleryTaskDispatcher()

    return RegisterService(
        user_repo=user_repo,
        tenant_repo=tenant_repo,
        hash_service=hash_service,
        email_service=email_service,
        cache_service=cache_service,  
        task_dispatcher=task_dispatcher,
    )


def get_login_service(db: Session = Depends(get_db)) -> LoginService:
    """
    Builds the LoginService so the Router doesn't have to.
    """
    user_repo = UserRepository(db)
    hash_service = BcryptHashService() 
    token_service = JwtService() 

    return LoginService(
        user_repo=user_repo, 
        hash_service=hash_service, 
        token_service=token_service
    )