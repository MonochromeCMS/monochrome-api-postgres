"""Create chapter model

Revision ID: f3a70f6f7132
Revises: 5ed03bc34ad9
Create Date: 2021-08-01 19:38:49.289578

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f3a70f6f7132'
down_revision = '5ed03bc34ad9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chapter',
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('volume', sa.Integer(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('manga_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chapter')
    # ### end Alembic commands ###
