# app/infrastructure/worker/tenant_tasks.py
import logging
from app.infrastructure.worker.celery_app import celery_app
from app.infrastructure.db.database import SessionLocal # Your project's sessionmaker factory
from app.infrastructure.db.tenant_provisioning import create_tenant_schema_and_migrate

logger = logging.getLogger("assistly")

@celery_app.task(name="tenant_create")
def tenant_create_task(tenant_subdomain: str):
    """
    Background task to provision a completely isolated PostgreSQL schema 
    and execute Alembic/SQLAlchemy migrations for a new tenant.
    """
    logger.info(f"Celery worker spinning up isolated provisioning thread for: '{tenant_subdomain}'")
    
    # Open a fresh database session inside the worker process
    db = SessionLocal()
    
    try:
        # Run the heavy schema creation and migration logic
        create_tenant_schema_and_migrate(db, tenant_subdomain)
        db.commit()
        
        logger.info(f"Database infrastructure successfully provisioned for tenant: '{tenant_subdomain}'")
        return f"Tenant schema '{tenant_subdomain}' is ready."
        
    except Exception as e:
        db.rollback()
        logger.error(f"Asynchronous provisioning crashed for tenant: '{tenant_subdomain}'", exc_info=True)
        # Re-raise the exception so Celery logs it as a failed task
        raise e
        
    finally:
        # Always close your connection pool references when finished
        db.close()