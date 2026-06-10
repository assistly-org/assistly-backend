import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command
from app.infrastructure.logger import logger

def create_tenant_schema_and_migrate(db_session: Session, subdomain: str):
    schema_name = f"tenant_{subdomain}"
    
    try:
        logger.info(f"Creating dynamic schema: {schema_name}")
        db_session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        db_session.commit()
        
        alembic_cfg = Config("alembic_tenant.ini")
        alembic_cfg.set_main_option("script_location", "alembic/tenant")
        alembic_cfg.set_main_option("version_locations", "alembic/tenant/versions")
        
        # ⚡ Pass the schema name to env.py via OS variables
        os.environ["TENANT_SCHEMA"] = schema_name 
        
        logger.info(f"Running Alembic migrations for schema: {schema_name}")
        command.upgrade(alembic_cfg, "head")
        logger.info(f"Successfully provisioned database for tenant: {subdomain}")
        
    except Exception as e:
        logger.error(f"Failed to provision schema for {subdomain}. Error: {e}")
        db_session.rollback()
        raise e
    finally:
        if "TENANT_SCHEMA" in os.environ:
            del os.environ["TENANT_SCHEMA"]