import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
# Import our background task from File 1
from app.infrastructure.worker.tenant_migration_tasks import migrate_single_tenant_schema

logger = logging.getLogger("assistly")

def migrate_all_existing_tenants(db: Session):
    """
    Finds all active tenants using raw SQL to bypass global ORM models,
    then chains execution states out into background message queues.
    """
    logger.info("Initializing enterprise multi-tenant migration dispatcher...")

    try:
        # 1. Grab only the slugs directly using raw SQL (lightning fast even for 10k rows)
        result = db.execute(text("SELECT slug FROM assistly_auth.tenant;"))
        slugs = [row[0] for row in result.fetchall()]
    except Exception as e:
        logger.error(f"❌ Failed to fetch tenant slugs from database. Error: {str(e)}")
        return

    if not slugs:
        logger.info("No existing tenants found to queue.")
        return

    logger.info(f"📊 Found {len(slugs)} tenants registered. Fanning out asynchronous tasks...")

    # 2. Push tasks instantly onto the Celery broker message line
    dispatched_count = 0
    for slug in slugs:
        migrate_single_tenant_schema.delay(slug)
        dispatched_count += 1

    logger.info(f"🎯 Distribution complete. Successfully dispatched {dispatched_count} tasks to Celery broker.")