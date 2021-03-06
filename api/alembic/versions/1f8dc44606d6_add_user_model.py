"""Add user model

Revision ID: 1f8dc44606d6
Revises: a5a3e07a92f6
Create Date: 2021-08-03 21:30:02.513181

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1f8dc44606d6'
down_revision = 'a5a3e07a92f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('username', sa.String(length=15), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
