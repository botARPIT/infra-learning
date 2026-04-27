from alembic import op
import sqlalchemy as sa


revision = "ad934d92ab0b"
down_revision = "cde7c7f374c4"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'jobs',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text('now()'),
        existing_nullable=False
    )

    op.alter_column(
        'jobs',
        'updated_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text('now()'),
        existing_nullable=False
    )


def downgrade():
    op.alter_column(
        'jobs',
        'updated_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False
    )

    op.alter_column(
        'jobs',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False
    )