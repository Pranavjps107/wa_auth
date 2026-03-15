"""Add full_name column to users

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('full_name', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('users', 'full_name')
