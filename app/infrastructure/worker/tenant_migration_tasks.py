import os
import logging
from alembic import command
from alembic.config import Config
from app.infrastructure.worker.celery_app import celery_app  # Ensure this points to your instantiated Celery app

logger = logging.getLogger("assistly")

@celery_app.task(
    name="tasks.migrate_single_tenant_schema",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    # ⚡ PRODUCTION GUARDRAIL: Smoothly limits worker processing throughput.
    # Celery will make sure across your entire cluster, at most 5 schemas per second start migrating.
    rate_limit="5/s"
)
def migrate_single_tenant_schema(self, slug: str):
    """
    Isolated, background worker task to upgrade a single schema.
    If one schema out of 10k fails, it retries independently without stalling others.
    """
    schema_name = f"tenant_{slug}"
    logger.info(f"🚀 Celery worker processing batch upgrade for: {schema_name}")

    # Calculate absolute base directory dynamically
    base_dir = os.path.abspath(os.getcwd())
    alembic_cfg = Config(os.path.join(base_dir, "alembic_tenant.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic/tenant"))

    try:
        # Set environment context target for env.py translation map
        os.environ["TENANT_SCHEMA"] = schema_name
        
        # Execute Alembic migrations programmatically inside this worker's isolated thread
        command.upgrade(alembic_cfg, "head")
        logger.info(f"✅ Successfully upgraded schema in background: {schema_name}")
        
    except Exception as e:
        logger.error(f"❌ Migration error encountered on schema {schema_name}: {str(e)}")
        try:
            # Retry task if it encountered a database deadlock or temporary lock check out issue
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.critical(f"💥 Max retries reached. Schema {schema_name} requires manual intervention.")
    finally:
        # Clean environment variables carefully
        os.environ.pop("TENANT_SCHEMA", None)