import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context
from dotenv import load_dotenv

# Import your database Base
from app.infrastructure.db.database import TenantBase
from app.infrastructure.models.tenant.booking import Booking

load_dotenv()
config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = TenantBase.metadata
tenant_schema = config.attributes.get('tenant_schema') or os.environ.get('TENANT_SCHEMA')

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return object.schema is None
    return True

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        if tenant_schema:
            connection.execute(text(f"SET search_path TO {tenant_schema}, public"))
            connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table="alembic_version_tenant",  
            version_table_schema=tenant_schema,
            include_object=include_object,
            include_schemas=False
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()