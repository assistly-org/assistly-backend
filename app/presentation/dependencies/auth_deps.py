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

from app.application.use_cases.auth.refresh_token import RefreshTokenService
from app.application.use_cases.auth.user_logout import LogoutService

from app.application.use_cases.auth.forgot_password import ForgotPasswordService
from app.application.use_cases.auth.verify_forgot_password import VerifyForgotPasswordService
from app.application.use_cases.auth.reset_password import ResetPasswordService
from app.application.use_cases.auth.change_password import ChangePasswordService

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
    tenant_repo = TenantRepository(db)
    hash_service = BcryptHashService() 
    token_service = JwtService() 

    return LoginService(
        user_repo=user_repo, 
        tenant_repo = tenant_repo,
        hash_service=hash_service, 
        token_service=token_service

    )

def get_refresh_service(db: Session = Depends(get_db)) -> RefreshTokenService:
    user_repo = UserRepository(db)
    token_service = JwtService()
    cache_service = RedisService() # ⚡ Initialize Redis
    
    return RefreshTokenService(
        user_repo=user_repo, 
        token_service=token_service,
        cache_service=cache_service # ⚡ Pass it in!
    )

def get_logout_service() -> LogoutService:
    # Notice we don't even need the database session for this! Just Redis.
    cache_service = RedisService()
    return LogoutService(cache_service=cache_service)


#------- FORGOT PASSWORD DEPENDENCIES -------#

def get_forgot_password_service(
    db: Session = Depends(get_db)
) -> ForgotPasswordService:

    user_repo = UserRepository(db)
    cache_service = RedisService()
    task_dispatcher = CeleryTaskDispatcher()

    return ForgotPasswordService(
        user_repo=user_repo,
        cache_service=cache_service,
        task_dispatcher=task_dispatcher
    )
    
    
def get_verify_forgot_password_service():
    cache_service = RedisService()

    return VerifyForgotPasswordService(
        cache_service=cache_service
    )
    


def get_reset_password_service(
    db: Session = Depends(get_db)
) -> ResetPasswordService:

    user_repo = UserRepository(db)
    hash_service = BcryptHashService()
    cache_service = RedisService()

    return ResetPasswordService(
        user_repo=user_repo,
        hash_service=hash_service,
        cache_service=cache_service
    )
    
    
#-------change password dependency-------#

def get_change_password_service(
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    hash_service = BcryptHashService()

    return ChangePasswordService(
        user_repo=user_repo,
        hash_service=hash_service
    )