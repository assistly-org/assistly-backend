from contextvars import ContextVar
from typing import Optional

# This creates a thread-safe variable to hold the schema name.
# It defaults to your global schema so global routes don't break.
current_tenant_schema: ContextVar[str] = ContextVar("current_tenant_schema", default="assistly_auth")

def set_tenant_schema(schema_name: str):
    """Helper to set the schema."""
    current_tenant_schema.set(schema_name)

def get_tenant_schema() -> str:
    """Helper to get the current schema."""
    return current_tenant_schema.get()