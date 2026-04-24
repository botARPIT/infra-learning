"""normalize timestamps to timestamptz

Revision ID: 9b0c6ad99049
Revises: b97c60bcfb8d
Create Date: 2026-04-25 00:34:30.393953
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '9b0c6ad99049'
down_revision: Union[str, Sequence[str], None] = 'b97c60bcfb8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'jobs',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=False),
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
        existing_nullable=False
    )

    op.alter_column(
        'jobs',
        'updated_at',
        existing_type=postgresql.TIMESTAMP(timezone=False),
        type_=sa.DateTime(timezone=True),
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
        existing_nullable=False
    )

    op.alter_column(
        'jobs',
        'claimed_at',
        existing_type=postgresql.TIMESTAMP(timezone=False),
        type_=sa.DateTime(timezone=True),
        postgresql_using="claimed_at AT TIME ZONE 'UTC'",
        existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        'jobs',
        'claimed_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(timezone=False),
        postgresql_using="claimed_at AT TIME ZONE 'UTC'",
        existing_nullable=True
    )

    op.alter_column(
        'jobs',
        'updated_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(timezone=False),
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
        existing_nullable=False
    )

    op.alter_column(
        'jobs',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(timezone=False),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
        existing_nullable=False
    )