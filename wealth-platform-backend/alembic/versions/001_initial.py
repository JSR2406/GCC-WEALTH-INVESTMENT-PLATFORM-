"""Initial migration - Create all core tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE bank_status_enum AS ENUM ('pending', 'active', 'suspended')")
    op.execute("CREATE TYPE revenue_model_enum AS ENUM ('saas', 'hybrid', 'aum_share')")
    op.execute("CREATE TYPE api_status_enum AS ENUM ('inactive', 'testing', 'active')")
    op.execute("CREATE TYPE kyc_status_enum AS ENUM ('pending', 'verified', 'rejected')")
    op.execute("CREATE TYPE subscription_tier_enum AS ENUM ('basic', 'premium')")
    op.execute("CREATE TYPE account_type_enum AS ENUM ('checking', 'savings', 'investment')")
    op.execute("CREATE TYPE goal_type_enum AS ENUM ('retirement', 'education', 'home', 'travel', 'emergency', 'custom')")
    op.execute("CREATE TYPE goal_status_enum AS ENUM ('active', 'paused', 'completed', 'cancelled')")
    op.execute("CREATE TYPE invoice_status_enum AS ENUM ('draft', 'sent', 'paid', 'overdue', 'cancelled')")
    op.execute("CREATE TYPE tax_report_type_enum AS ENUM ('fatca', 'crs', 'zakat', 'annual')")
    op.execute("CREATE TYPE audit_action_enum AS ENUM ('create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'import')")
    
    # Banks table
    op.create_table(
        'banks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('country', sa.String(2), nullable=False),
        sa.Column('revenue_model', postgresql.ENUM('saas', 'hybrid', 'aum_share', name='revenue_model_enum', create_type=False), nullable=False),
        sa.Column('base_fee_usd', sa.Numeric(10, 2)),
        sa.Column('aum_share_percentage', sa.Numeric(5, 2)),
        sa.Column('branding_config', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('api_key_hash', sa.String(255)),
        sa.Column('api_credentials', postgresql.JSONB),
        sa.Column('api_base_url', sa.String(500)),
        sa.Column('api_status', postgresql.ENUM('inactive', 'testing', 'active', name='api_status_enum', create_type=False), nullable=False, server_default='inactive'),
        sa.Column('analytics_access', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('data_sharing_agreement', postgresql.JSONB),
        sa.Column('status', postgresql.ENUM('pending', 'active', 'suspended', name='bank_status_enum', create_type=False), nullable=False, server_default='pending'),
        sa.Column('onboarded_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.CheckConstraint("country IN ('AE', 'SA')", name='ck_banks_country'),
    )
    op.create_index('idx_banks_country', 'banks', ['country'])
    op.create_index('idx_banks_status', 'banks', ['status'])
    
    # Bank Admins table
    op.create_table(
        'bank_admins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('bank_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('banks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('phone', sa.String(20)),
        sa.Column('role', sa.String(50), nullable=False, server_default='bank_admin'),
        sa.Column('permissions', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_email_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('bank_id', 'email', name='uq_bank_admins_bank_email'),
    )
    op.create_index('idx_bank_admins_bank_id', 'bank_admins', ['bank_id'])
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('bank_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('banks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('nationality', sa.String(2), nullable=False),
        sa.Column('residency_country', sa.String(2), nullable=False),
        sa.Column('kyc_status', postgresql.ENUM('pending', 'verified', 'rejected', name='kyc_status_enum', create_type=False), nullable=False, server_default='pending'),
        sa.Column('kyc_documents', postgresql.JSONB),
        sa.Column('kyc_verified_at', sa.DateTime(timezone=True)),
        sa.Column('emirates_id_encrypted', sa.String(500)),
        sa.Column('iqama_number_encrypted', sa.String(500)),
        sa.Column('tax_residency_countries', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('us_person', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('tin_numbers_encrypted', postgresql.JSONB),
        sa.Column('subscription_tier', postgresql.ENUM('basic', 'premium', name='subscription_tier_enum', create_type=False), nullable=False, server_default='basic'),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('external_id', sa.String(255)),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('onboarded_at', sa.DateTime(timezone=True)),
        sa.Column('last_active', sa.DateTime(timezone=True)),
        sa.Column('risk_profile', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('bank_id', 'email', name='uq_users_bank_email'),
        sa.CheckConstraint("residency_country IN ('AE', 'SA')", name='ck_users_residency_country'),
    )
    op.create_index('idx_users_bank_id', 'users', ['bank_id'])
    op.create_index('idx_users_kyc_status', 'users', ['kyc_status'])
    
    # User Accounts table
    op.create_table(
        'user_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('bank_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('banks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_account_id', sa.String(255), nullable=False),
        sa.Column('account_type', postgresql.ENUM('checking', 'savings', 'investment', name='account_type_enum', create_type=False), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('current_balance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('available_balance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('balance_usd', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('balance_updated_at', sa.DateTime(timezone=True)),
        sa.Column('holdings', postgresql.JSONB),
        sa.Column('iban', sa.String(50)),
        sa.Column('opened_date', sa.DateTime(timezone=True)),
        sa.Column('is_primary', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True)),
        sa.Column('sync_error', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('bank_id', 'external_account_id', name='uq_user_accounts_bank_external_id'),
    )
    op.create_index('idx_user_accounts_bank_id', 'user_accounts', ['bank_id'])
    op.create_index('idx_user_accounts_user_id', 'user_accounts', ['user_id'])


def downgrade() -> None:
    op.drop_table('user_accounts')
    op.drop_table('users')
    op.drop_table('bank_admins')
    op.drop_table('banks')
    
    op.execute('DROP TYPE IF EXISTS audit_action_enum')
    op.execute('DROP TYPE IF EXISTS tax_report_type_enum')
    op.execute('DROP TYPE IF EXISTS invoice_status_enum')
    op.execute('DROP TYPE IF EXISTS goal_status_enum')
    op.execute('DROP TYPE IF EXISTS goal_type_enum')
    op.execute('DROP TYPE IF EXISTS account_type_enum')
    op.execute('DROP TYPE IF EXISTS subscription_tier_enum')
    op.execute('DROP TYPE IF EXISTS kyc_status_enum')
    op.execute('DROP TYPE IF EXISTS api_status_enum')
    op.execute('DROP TYPE IF EXISTS revenue_model_enum')
    op.execute('DROP TYPE IF EXISTS bank_status_enum')
