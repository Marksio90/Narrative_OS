"""rename all metadata columns to avoid SQLAlchemy conflicts

Revision ID: 009
Revises: 008
Create Date: 2026-01-11 15:57:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """
    Rename all 'metadata' columns to avoid SQLAlchemy reserved name conflicts

    Affected tables:
    - chapters: metadata -> chapter_metadata
    - writing_sessions: metadata -> session_metadata
    - agent_tasks: metadata -> task_metadata
    - agent_conversations: metadata -> conversation_metadata
    - timeline_events: metadata -> event_metadata
    """
    # Chapters table
    op.alter_column('chapters', 'metadata', new_column_name='chapter_metadata')

    # Writing sessions table
    op.alter_column('writing_sessions', 'metadata', new_column_name='session_metadata')

    # Agent tasks table
    op.alter_column('agent_tasks', 'metadata', new_column_name='task_metadata')

    # Agent conversations table
    op.alter_column('agent_conversations', 'metadata', new_column_name='conversation_metadata')

    # Timeline events table
    op.alter_column('timeline_events', 'metadata', new_column_name='event_metadata')


def downgrade():
    """Revert all column names back to 'metadata'"""
    # Chapters table
    op.alter_column('chapters', 'chapter_metadata', new_column_name='metadata')

    # Writing sessions table
    op.alter_column('writing_sessions', 'session_metadata', new_column_name='metadata')

    # Agent tasks table
    op.alter_column('agent_tasks', 'task_metadata', new_column_name='metadata')

    # Agent conversations table
    op.alter_column('agent_conversations', 'conversation_metadata', new_column_name='metadata')

    # Timeline events table
    op.alter_column('timeline_events', 'event_metadata', new_column_name='metadata')
