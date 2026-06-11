import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
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
        pool_pre_ping=True
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
        
        # 1. Check if we ALREADY validated this tenant in memory
        if target_schema not in VALIDATED_SCHEMAS:
            
            # 2. Use pg_namespace (10x faster than information_schema)
            schema_exists = db.execute(
                text("SELECT 1 FROM pg_namespace WHERE nspname = :schema"),
                {"schema": target_schema}
            ).scalar()

            # 3. Block if fake
            if not schema_exists:
                logger.warning(f"Blocked request to non-existent tenant: {target_schema}")
                raise HTTPException(status_code=404, detail="Tenant workspace not found.")
            
            # 4. Cache it
            VALIDATED_SCHEMAS.add(target_schema)
            logger.info(f"⚡ Cached valid tenant schema in memory: {target_schema}")
            
        # 5. Switch schema safely
        db.execute(text(f"SET search_path TO {target_schema}"))
             
        yield db
        
    finally:
        # ⚡ CRITICAL FIX: Clean the connection before giving it back to the pool
        db.execute(text("RESET search_path")) 
        db.close()