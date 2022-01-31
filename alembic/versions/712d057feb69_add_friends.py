"""add friends

Revision ID: 712d057feb69
Revises: 
Create Date: 2022-01-16 15:01:04.526080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '712d057feb69'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=45), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=45), nullable=False),
    sa.Column('email', sa.String(length=45), nullable=False),
    sa.Column('password', sa.String(length=160), nullable=False),
    sa.Column('city', sa.String(length=40), nullable=False),
    sa.Column('photo', sa.BLOB(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('friends',
    sa.Column('user_id_1', sa.Integer(), nullable=False),
    sa.Column('user_id_2', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('new', 'accepted', 'declined'), nullable=False),
    sa.ForeignKeyConstraint(['user_id_1'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id_2'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id_1', 'user_id_2')
    )
    op.create_table('wall',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('text', sa.String(length=500), nullable=False),
    sa.Column('photo_wall', sa.BLOB(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wall')
    op.drop_table('friends')
    op.drop_table('user')
    op.drop_table('genre')
    # ### end Alembic commands ###
