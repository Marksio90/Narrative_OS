"""rename planner chapters table

Revision ID: 010
Revises: 009
Create Date: 2026-01-11

Renames 'chapters' table used by planner.py to 'planned_chapters'
to avoid conflict with manuscript 'chapters' table from chapter.py
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Note: This migration assumes the 'chapters' table from planner.py
    # was never created in production. If it exists, we need to check
    # which one it is before renaming.

    # Check if planned_chapters already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'planned_chapters' not in existing_tables and 'book_arcs' in existing_tables:
        # The planner chapters table exists, rename it
        op.rename_table('chapters', 'planned_chapters')

        # Update foreign key in scenes table
        with op.batch_alter_table('scenes', schema=None) as batch_op:
            batch_op.drop_constraint('scenes_chapter_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key(
                'scenes_chapter_id_fkey',
                'planned_chapters',
                ['chapter_id'],
                ['id']
            )


def downgrade() -> None:
    # Rename back to chapters
    op.rename_table('planned_chapters', 'chapters')

    # Update foreign key in scenes table
    with op.batch_alter_table('scenes', schema=None) as batch_op:
        batch_op.drop_constraint('scenes_chapter_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'scenes_chapter_id_fkey',
            'chapters',
            ['chapter_id'],
            ['id']
        )
