"""create wall table

Revision ID: 38d4e07ace2d
Revises: 03451c203018
Create Date: 2022-01-13 18:50:48.191067

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '38d4e07ace2d'
down_revision = '03451c203018'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('wall',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), sa.ForeignKey('user_id'), nullable=False),
                    sa.Column('username', sa.String(length=45), sa.ForeignKey('username'), nullable=False),
                    sa.Column('photo', sa.BLOB(), sa.ForeignKey('photo'), nullable=True),
                    sa.Column('genre_id', sa.Integer(), sa.ForeignKey('genre_id'), nullable=False),
                    sa.Column('datetime', sa.DateTime(), nullable=False),
                    sa.Column('text', sa.Text, nullable=False),
                    sa.Column('photo_wall', sa.BLOB(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    pass
