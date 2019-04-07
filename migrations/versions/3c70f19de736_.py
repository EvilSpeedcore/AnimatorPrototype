"""empty message

Revision ID: 3c70f19de736
Revises: 
Create Date: 2019-04-07 15:04:27.183232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c70f19de736'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('siteuser', 'age')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('siteuser', sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
