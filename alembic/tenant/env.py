import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context
from dotenv import load_dotenv
from app.infrastructure.models.tenant.booking import Booking

# Import your database Base
from app.infrastructure.db.database import TenantBase

load_dotenv()
config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = TenantBase.metadata

# 1. Catch the dynamic schema name passed from our provisioning script
tenant_schema = config.attributes.get("tenant_schema")


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter to ensure we don't accidentally create global tables (like Users)
    inside the dynamic tenant schemas.
    """
    if type_ == "table":
        # Only include tables that DO NOT have a hardcoded schema
        return object.schema is None
    return True


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        # 2. THE MAGIC: Switch PostgreSQL to the dynamic tenant schema
        if tenant_schema:
            connection.execute(text(f"SET search_path TO {tenant_schema}"))

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # 3. Store the alembic_version table inside the tenant's schema
            version_table_schema=tenant_schema,
            include_object=include_object,
            include_schemas=False,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()



