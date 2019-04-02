"""empty message

Revision ID: 1b7aa3ffea77
Revises: 
Create Date: 2019-03-10 20:02:05.021080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b7aa3ffea77'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('topanime',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('anime_type', sa.String(), nullable=True),
    sa.Column('episodes', sa.String(), nullable=True),
    sa.Column('studio', sa.String(), nullable=True),
    sa.Column('src', sa.String(), nullable=True),
    sa.Column('genre', sa.String(), nullable=True),
    sa.Column('score', sa.String(), nullable=True),
    sa.Column('synopsis', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('topanime')
    # ### end Alembic commands ###