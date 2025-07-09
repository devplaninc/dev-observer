"""Add changes summary table

Revision ID: d98344101151
Revises: 4c50529cbb71
Create Date: 2025-07-08 17:00:46.008302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd98344101151'
down_revision: Union[str, None] = '4c50529cbb71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('changes_summary',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('repo_id', sa.String(), nullable=False),
        sa.Column('repo_full_name', sa.String(), nullable=False),
        sa.Column('json_data', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_changes_summary_repo_id'), 'changes_summary', ['repo_id'], unique=False)
    op.create_index(op.f('ix_changes_summary_repo_full_name'), 'changes_summary', ['repo_full_name'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_changes_summary_repo_full_name'), table_name='changes_summary')
    op.drop_index(op.f('ix_changes_summary_repo_id'), table_name='changes_summary')
    op.drop_table('changes_summary')
