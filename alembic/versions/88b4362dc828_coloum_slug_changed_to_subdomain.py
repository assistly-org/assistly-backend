"""Coloum slug changed to subdomain

Revision ID: 88b4362dc828
Revises: 9e6c922bc035
Create Date: 2026-06-30 15:40:16.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88b4362dc828'
down_revision: Union[str, None] = '9e6c922bc035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename 'slug' to 'subdomain' in tenants table
    op.alter_column('tenants', 'slug', new_column_name='subdomain', schema='assistly_auth')
    
    # 2. Update the unique constraints for the tenants table
    op.drop_constraint('tenants_slug_key', 'tenants', schema='assistly_auth', type_='unique')
    op.create_unique_constraint('tenants_subdomain_key', 'tenants', ['subdomain'], schema='assistly_auth')

    # 3. Rename the tracking column in the users table
    op.alter_column('users', 'last_active_tenant_slug', new_column_name='last_active_tenant_subdomain', schema='assistly_auth')


def downgrade() -> None:
    # 1. Revert users table column
    op.alter_column('users', 'last_active_tenant_subdomain', new_column_name='last_active_tenant_slug', schema='assistly_auth')

    # 2. Revert unique constraints
    op.drop_constraint('tenants_subdomain_key', 'tenants', schema='assistly_auth', type_='unique')
    op.create_unique_constraint('tenants_slug_key', 'tenants', ['slug'], schema='assistly_auth')

    # 3. Revert tenants table column
    op.alter_column('tenants', 'subdomain', new_column_name='slug', schema='assistly_auth')