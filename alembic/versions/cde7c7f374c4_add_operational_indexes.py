from typing import Sequence, Union

from alembic import op


revision = "cde7c7f374c4"
down_revision = "9b0c6ad99049"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('idx_jobs_status', 'jobs', ['status'])
    op.create_index('idx_jobs_last_heartbeat_at', 'jobs', ['last_heartbeat_at'])
    op.create_index('idx_jobs_claimed_at', 'jobs', ['claimed_at'])


def downgrade() -> None:
    op.drop_index('idx_jobs_claimed_at', table_name='jobs')
    op.drop_index('idx_jobs_last_heartbeat_at', table_name='jobs')
    op.drop_index('idx_jobs_status', table_name='jobs')