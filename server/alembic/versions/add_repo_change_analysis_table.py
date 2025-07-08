"""add repo_change_analysis table

Revision ID: add_repo_change_analysis
Revises: 4c50529cbb71
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_repo_change_analysis'
down_revision: Union[str, None] = '4c50529cbb71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('repo_change_analysis',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('repo_id', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('observation_key', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repo_change_analysis_repo_id'), 'repo_change_analysis', ['repo_id'], unique=False)
    op.create_index(op.f('ix_repo_change_analysis_status'), 'repo_change_analysis', ['status'], unique=False)
    op.create_index(op.f('ix_repo_change_analysis_analyzed_at'), 'repo_change_analysis', ['analyzed_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_repo_change_analysis_analyzed_at'), table_name='repo_change_analysis')
    op.drop_index(op.f('ix_repo_change_analysis_status'), table_name='repo_change_analysis')
    op.drop_index(op.f('ix_repo_change_analysis_repo_id'), table_name='repo_change_analysis')
    op.drop_table('repo_change_analysis')