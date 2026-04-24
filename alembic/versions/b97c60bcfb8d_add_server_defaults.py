"""add server defaults

Revision ID: b97c60bcfb8d
Revises: 1260a22374d0
Create Date: 2026-04-25 00:31:18.887845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b97c60bcfb8d'
down_revision: Union[str, Sequence[str], None] = '1260a22374d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'jobs',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text('now()'),
        existing_nullable=False
    )

    op.alter_column(
        'jobs',
        'updated_at',
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text('now()'),
        existing_nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'jobs',
        'updated_at',
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_nullable=False
    )

    op.alter_column(
        'jobs',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_nullable=False
    )
