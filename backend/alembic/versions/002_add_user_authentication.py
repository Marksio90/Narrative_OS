"""Add user authentication tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-07

Modern authentication system with FastAPI-Users
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'  # Replace with your last migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create subscription tier enum
    subscription_tier_enum = postgresql.ENUM(
        'free', 'pro', 'studio',
        name='subscriptiontier',
        create_type=True
    )
    subscription_tier_enum.create(op.get_bind(), checkfirst=True)

    # Create collaborator role enum
    collaborator_role_enum = postgresql.ENUM(
        'owner', 'editor', 'writer', 'viewer',
        name='collaboratorrole',
        create_type=True
    )
    collaborator_role_enum.create(op.get_bind(), checkfirst=True)

    # === Create users table ===
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),

        # Custom fields
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),

        # Subscription
        sa.Column('subscription_tier', subscription_tier_enum, nullable=False, server_default='free'),
        sa.Column('subscription_expires_at', sa.DateTime(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),

        # Usage tracking
        sa.Column('llm_calls_this_month', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('storage_used_bytes', sa.Integer(), nullable=False, server_default='0'),

        # Audit
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_ip', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('stripe_customer_id')
    )

    # Indexes for users
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_subscription_tier', 'users', ['subscription_tier'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    # === Create OAuth accounts table ===
    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('oauth_name', sa.String(length=50), nullable=False),
        sa.Column('access_token', sa.String(length=500), nullable=False),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('account_id', sa.String(length=320), nullable=False),
        sa.Column('account_email', sa.String(length=320), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    op.create_index('ix_oauth_accounts_user_id', 'oauth_accounts', ['user_id'])
    op.create_index('ix_oauth_accounts_oauth_name', 'oauth_accounts', ['oauth_name'])

    # === Create project_collaborators table ===
    op.create_table(
        'project_collaborators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', collaborator_role_enum, nullable=False),
        sa.Column('invited_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        # Note: project_id FK will be added after projects table is updated
    )

    op.create_index('ix_project_collaborators_project_id', 'project_collaborators', ['project_id'])
    op.create_index('ix_project_collaborators_user_id', 'project_collaborators', ['user_id'])
    op.create_index('ix_project_collaborators_role', 'project_collaborators', ['role'])

    # === Update projects table ===
    # Add owner_id and visibility columns
    op.add_column('projects', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('visibility', sa.String(length=20), nullable=False, server_default='private'))

    # Create foreign key
    op.create_foreign_key('fk_projects_owner', 'projects', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_projects_owner_id', 'projects', ['owner_id'])

    # === Add soft delete columns to all major tables ===
    tables_to_soft_delete = [
        'projects', 'characters', 'locations', 'factions', 'magic_rules',
        'items', 'events', 'promises', 'threads', 'style_profiles',
        'book_arcs', 'chapters', 'scenes', 'canon_contracts'
    ]

    for table_name in tables_to_soft_delete:
        # Check if table exists first
        try:
            op.add_column(table_name, sa.Column('deleted_at', sa.DateTime(), nullable=True))
            op.add_column(table_name, sa.Column('deleted_by', sa.Integer(), nullable=True))
            op.create_index(f'ix_{table_name}_deleted_at', table_name, ['deleted_at'])
            op.create_foreign_key(
                f'fk_{table_name}_deleted_by',
                table_name,
                'users',
                ['deleted_by'],
                ['id'],
                ondelete='SET NULL'
            )
        except Exception as e:
            print(f"Skipping {table_name}: {e}")


def downgrade() -> None:
    # Remove soft delete columns
    tables_to_restore = [
        'projects', 'characters', 'locations', 'factions', 'magic_rules',
        'items', 'events', 'promises', 'threads', 'style_profiles',
        'book_arcs', 'chapters', 'scenes', 'canon_contracts'
    ]

    for table_name in tables_to_restore:
        try:
            op.drop_constraint(f'fk_{table_name}_deleted_by', table_name, type_='foreignkey')
            op.drop_index(f'ix_{table_name}_deleted_at', table_name)
            op.drop_column(table_name, 'deleted_by')
            op.drop_column(table_name, 'deleted_at')
        except:
            pass

    # Drop projects updates
    op.drop_constraint('fk_projects_owner', 'projects', type_='foreignkey')
    op.drop_index('ix_projects_owner_id', 'projects')
    op.drop_column('projects', 'visibility')
    op.drop_column('projects', 'owner_id')

    # Drop tables
    op.drop_index('ix_project_collaborators_role', 'project_collaborators')
    op.drop_index('ix_project_collaborators_user_id', 'project_collaborators')
    op.drop_index('ix_project_collaborators_project_id', 'project_collaborators')
    op.drop_table('project_collaborators')

    op.drop_index('ix_oauth_accounts_oauth_name', 'oauth_accounts')
    op.drop_index('ix_oauth_accounts_user_id', 'oauth_accounts')
    op.drop_table('oauth_accounts')

    op.drop_index('ix_users_created_at', 'users')
    op.drop_index('ix_users_subscription_tier', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')

    # Drop enums
    sa.Enum(name='collaboratorrole').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptiontier').drop(op.get_bind(), checkfirst=True)
