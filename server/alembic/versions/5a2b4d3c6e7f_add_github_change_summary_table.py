"""add github change summary table

Revision ID: 5a2b4d3c6e7f
Revises: 4c50529cbb71
Create Date: 2025-07-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a2b4d3c6e7f'
down_revision: Union[str, None] = '4c50529cbb71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('github_change_summary',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('repo_id', sa.String(), nullable=False),
    sa.Column('commit_sha', sa.String(), nullable=False),
    sa.Column('analysis_type', sa.String(), nullable=False),
    sa.Column('summary', sa.String(), nullable=False),
    sa.Column('changes_data', sa.String(), nullable=False),
    sa.Column('analysis_period_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('analysis_period_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_github_change_summary_repo_id'), 'github_change_summary', ['repo_id'], unique=False)
    op.create_index(op.f('ix_github_change_summary_commit_sha'), 'github_change_summary', ['commit_sha'], unique=False)
    op.create_index(op.f('ix_github_change_summary_analysis_type'), 'github_change_summary', ['analysis_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_github_change_summary_analysis_type'), table_name='github_change_summary')
    op.drop_index(op.f('ix_github_change_summary_commit_sha'), table_name='github_change_summary')
    op.drop_index(op.f('ix_github_change_summary_repo_id'), table_name='github_change_summary')
    op.drop_table('github_change_summary')