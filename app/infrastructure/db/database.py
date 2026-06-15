import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
from fastapi import HTTPException
from app.infrastructure.logger import logger 
from app.infrastructure.db.tenant_context import get_tenant_schema

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set! Shutting down.")
    raise ValueError("DATABASE_URL environment variable is not set!")

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=False,
        poolclass=NullPool
    )
    logger.info("Database engine configured successfully.")
except Exception as e:
    logger.critical(f"Failed to configure database engine: {e}")
    raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===========================
# For Auth and commen tables
#============================
class Base(DeclarativeBase):
    """Used ONLY for Global models (Users, Tenants)"""
    pass
# ==========================
# For Tenant based tables
#===========================
class TenantBase(DeclarativeBase):
    """Used ONLY for Tenant-specific models (Products, Customers, etc.)"""
    pass

# ⚡ THE SPEED UP: In-Memory Cache for validated schemas
VALIDATED_SCHEMAS = set(["assistly_auth", "public"])

def get_db():
    db = SessionLocal()
    try:
        target_schema = get_tenant_schema()
        
        if target_schema not in VALIDATED_SCHEMAS:
            schema_exists = db.execute(
                text("SELECT 1 FROM pg_namespace WHERE nspname = :schema"),
                {"schema": target_schema}
            ).scalar()

            if not schema_exists:
                logger.warning(f"Blocked request to non-existent tenant: {target_schema}")
                raise HTTPException(status_code=404, detail="Tenant workspace not found.")
            
            VALIDATED_SCHEMAS.add(target_schema)
            logger.info(f"⚡ Cached valid tenant schema: {target_schema}")
            
        db.execute(text(f"SET LOCAL search_path TO {target_schema}"))
        yield db
        
    finally:
        db.close()