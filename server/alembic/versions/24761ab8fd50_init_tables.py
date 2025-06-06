"""init tables

Revision ID: 24761ab8fd50
Revises: 
Create Date: 2025-06-04 10:00:46.296747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24761ab8fd50'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('git_repo',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('json_data', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('global_config',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('json_data', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('processing_item',
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('json_data', sa.String(), nullable=False),
    sa.Column('next_processing', sa.DateTime(), nullable=True),
    sa.Column('last_processed', sa.DateTime(), nullable=True),
    sa.Column('last_error', sa.String(), nullable=True),
    sa.Column('no_processing', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('processing_item')
    op.drop_table('global_config')
    op.drop_table('git_repo')
    # ### end Alembic commands ###
