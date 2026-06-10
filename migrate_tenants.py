# migrate_tenants.py
import logging
from app.infrastructure.db.database import SessionLocal
from app.infrastructure.db.tenant_migration_service import migrate_all_existing_tenants

# Set root logging visualization
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    db = SessionLocal()
    try:
        migrate_all_existing_tenants(db)
    finally:
        db.close()