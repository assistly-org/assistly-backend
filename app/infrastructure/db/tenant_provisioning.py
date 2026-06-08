from sqlalchemy import text
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command
from app.infrastructure.logger import logger


def create_tenant_schema_and_migrate(db_session: Session, subdomain: str):
    schema_name = f"tenant_{subdomain}"
    
    try:
        # 1. Create the empty schema (using SQLAlchemy's text() construct)
        logger.info(f"Creating dynamic schema: {schema_name}")
        db_session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        db_session.commit()
        
        # 2. Tell Alembic to target the specific tenant blueprint folder
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "alembic/tenant")
        
        # 3. Pass the schema name dynamically to the tenant's env.py
        alembic_cfg.attributes['tenant_schema'] = schema_name 
        
        # 4. Run the upgrade programmatically
        logger.info(f"Running Alembic migrations for schema: {schema_name}")
        command.upgrade(alembic_cfg, "head")
        logger.info(f"Successfully provisioned database for tenant: {subdomain}")
        
    except Exception as e:
        logger.error(f"Failed to provision schema for {subdomain}. Error: {e}")
        db_session.rollback()
        raise e