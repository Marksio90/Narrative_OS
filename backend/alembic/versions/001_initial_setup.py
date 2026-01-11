"""Initial database setup

Revision ID: 001
Revises: None
Create Date: 2026-01-07

Creates basic project structure and tables
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '001'
down_revision = None  # This is the first migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables"""

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.Column('target_word_count', sa.Integer(), nullable=True, server_default='80000'),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='draft'),
        sa.Column('project_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_genre'), 'projects', ['genre'], unique=False)
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)

    # Create canon_versions table
    op.create_table(
        'canon_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('commit_message', sa.Text(), nullable=True),
        sa.Column('parent_version_id', sa.Integer(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('changes', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['parent_version_id'], ['canon_versions.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_canon_versions_id'), 'canon_versions', ['id'], unique=False)
    op.create_index(op.f('ix_canon_versions_project_id'), 'canon_versions', ['project_id'], unique=False)


def downgrade() -> None:
    """Drop initial tables"""
    op.drop_index(op.f('ix_canon_versions_project_id'), table_name='canon_versions')
    op.drop_index(op.f('ix_canon_versions_id'), table_name='canon_versions')
    op.drop_table('canon_versions')

    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_genre'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
