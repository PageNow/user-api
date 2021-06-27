"""Added gender
Revision ID: ff860b5621fc
Revises: cbaf738e6d65
Create Date: 2021-06-27 00:39:31.421357
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'ff860b5621fc'
down_revision = 'cbaf738e6d65'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_info', sa.Column('gender', sa.String(), nullable=False))
    op.add_column('user_info', sa.Column('gender_public', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_info', 'gender_public')
    op.drop_column('user_info', 'gender')
    # ### end Alembic commands ###