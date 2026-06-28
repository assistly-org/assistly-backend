from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.auth.bcrypt_hash_service import BcryptHashService
from app.infrastructure.worker.celery_dispatcher import CeleryTaskDispatcher
from app.application.use_cases.tenant.tenant_setup import TenantSetupService
from app.application.use_cases.organization.list_tenants import ListTenantsService
from app.infrastructure.repositories.agent_repository import AgentRepository
from app.application.use_cases.agent.process_action import ProcessAgentActionUseCase


def get_tenant_setup_service(db: Session = Depends(get_db)) -> TenantSetupService:
    return TenantSetupService(
        db=db,
        tenant_repo=TenantRepository(db),
        user_repo=UserRepository(db),
        hash_service=BcryptHashService(),  # ⚡ Added the Hash Service
        task_dispatcher=CeleryTaskDispatcher()
    )


def get_tenant_repository(db: Session = Depends(get_db)) -> TenantRepository:
    return TenantRepository(db)


def get_list_tenants_service(
    repo: TenantRepository = Depends(get_tenant_repository),
) -> ListTenantsService:
    return ListTenantsService(repo)


# Add this to the bottom of app/presentation/dependencies/tenant_deps.py


def get_agent_action_service(
    db: Session = Depends(get_db),
) -> ProcessAgentActionUseCase:
    # 1. Open the database channel
    repo = AgentRepository(db_session=db)
    # 2. Hand it to the AI use case engine
    return ProcessAgentActionUseCase(agent_repo=repo)
