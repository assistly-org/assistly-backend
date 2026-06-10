from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# --- ADD THESE 4 LINES ---
import os
from dotenv import load_dotenv
from app.infrastructure.db.database import Base
from app.infrastructure.models.auth.users import User
from app.infrastructure.models.auth.tenants import Tenant
from app.infrastructure.models.auth.addresses import Address 

# Load environment variables
load_dotenv()
# -------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- ADD THIS LINE TO INJECT YOUR SUPABASE URL ---
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
# -------------------------------------------------

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- MODIFY THIS LINE TO USE YOUR BASE METADATA ---
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_name(name, type_, parent_names):
    if type_ == "schema":
        # ONLY allow Alembic to look at 'public' and 'assistly_auth'
        return name in [None, "public", "assistly_auth"]
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()




def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,  # <-- ADD THIS LINE
            include_name=include_name,
            version_table_schema='assistly_auth'
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
