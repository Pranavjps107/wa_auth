"""Add missing columns to match database schema

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to tenants
    op.add_column('tenants', sa.Column('subdomain', sa.String(100), nullable=True))
    op.add_column('tenants', sa.Column('status', sa.String(20), server_default='active', nullable=False))
    op.create_unique_constraint('uq_tenants_subdomain', 'tenants', ['subdomain'])
    op.create_check_constraint('tenant_status_valid', 'tenants', "status IN ('active', 'suspended', 'deleted')")
    
    # Add missing columns to users
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('users', sa.Column('status', sa.String(20), server_default='active', nullable=False))
    op.add_column('users', sa.Column('email_verified', sa.Boolean, server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer, server_default='0', nullable=False))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    
    # Add constraints to users
    op.create_check_constraint('users_email_lowercase', 'users', 'email = lower(email)')
    op.create_check_constraint('users_status_valid', 'users', "status IN ('active', 'inactive', 'suspended')")
    
    # Add missing column to api_keys
    op.add_column('api_keys', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
    op.create_check_constraint('api_keys_name_length', 'api_keys', 'char_length(name) > 0')
    
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean, server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('idx_refresh_tokens_hash', 'refresh_tokens', ['token_hash'])
    op.create_index('idx_refresh_tokens_user', 'refresh_tokens', ['user_id'])


def downgrade():
    # Drop refresh_tokens table
    op.drop_index('idx_refresh_tokens_user', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_hash', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    
    # Remove columns from api_keys
    op.drop_constraint('api_keys_name_length', 'api_keys')
    op.drop_column('api_keys', 'expires_at')
    
    # Remove constraints and columns from users
    op.drop_constraint('users_status_valid', 'users')
    op.drop_constraint('users_email_lowercase', 'users')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'status')
    op.drop_column('users', 'updated_at')
    
    # Remove constraints and columns from tenants
    op.drop_constraint('tenant_status_valid', 'tenants')
    op.drop_constraint('uq_tenants_subdomain', 'tenants')
    op.drop_column('tenants', 'status')
    op.drop_column('tenants', 'subdomain')
