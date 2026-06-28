"""add_agent_engine_tables

Revision ID: 9b315d9b3aaa
Revises: cfdd81a424ef
Create Date: 2026-06-26 11:49:38.224690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9b315d9b3aaa'
down_revision: Union[str, Sequence[str], None] = 'cfdd81a424ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    return inspect(op.get_bind()).has_table(table_name)


def upgrade() -> None:
    """Upgrade schema."""
    if not _has_table('omnichannel_sessions'):
        op.create_table(
            'omnichannel_sessions',
            sa.Column('session_id', sa.String(), nullable=False),
            sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('bot_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('primary_phone', sa.String(length=20), nullable=True),
            sa.Column('channel_source', sa.String(length=50), nullable=False),
            sa.Column(
                'conversation_state',
                sa.String(length=30),
                server_default='idle',
                nullable=False,
            ),
            sa.Column('active_action', sa.String(length=50), nullable=True),
            sa.Column(
                'active_context',
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('session_id'),
        )
        op.create_index(
            'ix_omnichannel_sessions_bot_id',
            'omnichannel_sessions',
            ['bot_id'],
            unique=False,
        )
        op.create_index(
            'ix_omnichannel_sessions_session_id',
            'omnichannel_sessions',
            ['session_id'],
            unique=False,
        )
        op.create_index(
            'ix_omnichannel_sessions_tenant_id',
            'omnichannel_sessions',
            ['tenant_id'],
            unique=False,
        )

    if not _has_table('lead_captures'):
        op.create_table(
            'lead_captures',
            sa.Column('id', sa.String(length=50), nullable=False),
            sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('bot_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('session_id', sa.String(), nullable=True),
            sa.Column('full_name', sa.String(length=255), nullable=True),
            sa.Column('phone', sa.String(length=20), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column(
                'metadata_fields',
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(
                ['session_id'],
                ['omnichannel_sessions.session_id'],
                ondelete='SET NULL',
            ),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_lead_captures_bot_id', 'lead_captures', ['bot_id'], unique=False)
        op.create_index('ix_lead_captures_id', 'lead_captures', ['id'], unique=False)
        op.create_index('ix_lead_captures_tenant_id', 'lead_captures', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text('DROP INDEX IF EXISTS ix_lead_captures_tenant_id'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_lead_captures_id'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_lead_captures_bot_id'))
    op.execute(sa.text('DROP TABLE IF EXISTS lead_captures'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_omnichannel_sessions_tenant_id'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_omnichannel_sessions_session_id'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_omnichannel_sessions_bot_id'))
    op.execute(sa.text('DROP TABLE IF EXISTS omnichannel_sessions'))
