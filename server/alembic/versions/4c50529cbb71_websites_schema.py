"""websites_schema

Revision ID: 4c50529cbb71
Revises: 3284831721ef
Create Date: 2025-06-26 22:28:01.762295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c50529cbb71'
down_revision: Union[str, None] = '3284831721ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('web_site',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('json_data', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_web_site_url'), 'web_site', ['url'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_web_site_url'), table_name='web_site')
    op.drop_table('web_site')
    # ### end Alembic commands ###
