from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.auth.bcrypt_hash_service import BcryptHashService
from app.infrastructure.worker.celery_dispatcher import CeleryTaskDispatcher
from app.application.use_cases.tenant.tenant_setup import TenantSetupService

def get_tenant_setup_service(db: Session = Depends(get_db)) -> TenantSetupService:
    return TenantSetupService(
        db=db,
        tenant_repo=TenantRepository(db),
        user_repo=UserRepository(db),
        hash_service=BcryptHashService(), # ⚡ Added the Hash Service
        task_dispatcher=CeleryTaskDispatcher()
    )