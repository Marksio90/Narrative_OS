"""rename project metadata column

Revision ID: 008
Revises: 007
Create Date: 2026-01-11 13:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """Rename metadata column to project_metadata to avoid SQLAlchemy reserved name conflict"""
    # Rename column from 'metadata' to 'project_metadata'
    op.alter_column('projects', 'metadata', new_column_name='project_metadata')


def downgrade():
    """Revert column name back to metadata"""
    op.alter_column('projects', 'project_metadata', new_column_name='metadata')
