# app/presentation/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session

# Import your database session provider (adjust the path if yours is different)
from app.infrastructure.db.database import get_db

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.infrastructure.auth.bcrypt_hash_service import BcryptHashService

# Import your RegisterService (adjust path depending on where you saved it)
from app.application.use_cases.user_register import RegisterService

# Add this import at the top of your file
from app.application.use_cases.verify_user import VerifyService

# ... (your existing get_register_service code) ...
from app.infrastructure.email.smtp_services import EmailService


def get_verify_service(db: Session = Depends(get_db)) -> VerifyService:
    """
    Builds and returns a fully initialized VerifyService.
    FastAPI will automatically run this whenever the /verify route is called.
    """
    # 1. Initialize the Repositories with the current database session
    user_repo = UserRepository(db)
    tenant_repo = TenantRepository(db)

    # 2. Inject the dependencies into the VerifyService
    return VerifyService(user_repo=user_repo, tenant_repo=tenant_repo)


def get_register_service(db: Session = Depends(get_db)) -> RegisterService:
    """
    Builds and returns a fully initialized RegisterService.
    FastAPI will automatically run this whenever a route requests it.
    """
    # 1. Provide the DB session to the Repositories
    user_repo = UserRepository(db)
    tenant_repo = TenantRepository(db)
    email_service = EmailService()  # <-- Initialize it here

    # 2. Initialize the Hash Service
    hash_service = BcryptHashService()

    # 3. Inject all dependencies into the Service
    return RegisterService(
        user_repo=user_repo,
        tenant_repo=tenant_repo,
        hash_service=hash_service,
        email_service=email_service,
    )
