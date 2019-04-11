"""empty message

Revision ID: c2934e733f54
Revises: 
Create Date: 2019-04-07 15:35:48.775853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2934e733f54'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('siteuser',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('privilege', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
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
    op.create_table('profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mal_username', sa.String(), nullable=True),
    sa.Column('list', sa.String(), nullable=False),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['siteuser.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recommendations',
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
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['siteuser.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('statistics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('accepted_anime_number', sa.Integer(), nullable=True),
    sa.Column('denied_anime_number', sa.Integer(), nullable=True),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['siteuser.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('statistics')
    op.drop_table('recommendations')
    op.drop_table('profile')
    op.drop_table('topanime')
    op.drop_table('siteuser')
    # ### end Alembic commands ###