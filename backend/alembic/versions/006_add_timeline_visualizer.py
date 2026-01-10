"""add timeline visualizer

Revision ID: 006
Revises: 005
Create Date: 2026-01-10 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    timeline_event_type_enum = postgresql.ENUM(
        'chapter', 'story_event', 'milestone', 'beat', 'consequence', 'custom',
        name='timelineeventtype',
        create_type=True
    )
    timeline_event_type_enum.create(op.get_bind(), checkfirst=True)

    timeline_layer_enum = postgresql.ENUM(
        'plot', 'character', 'theme', 'technical', 'consequence',
        name='timelinelayer',
        create_type=True
    )
    timeline_layer_enum.create(op.get_bind(), checkfirst=True)

    conflict_type_enum = postgresql.ENUM(
        'overlap', 'inconsistency', 'pacing_issue', 'character_conflict', 'continuity_error',
        name='conflicttype',
        create_type=True
    )
    conflict_type_enum.create(op.get_bind(), checkfirst=True)

    conflict_severity_enum = postgresql.ENUM(
        'info', 'warning', 'error', 'critical',
        name='conflictseverity',
        create_type=True
    )
    conflict_severity_enum.create(op.get_bind(), checkfirst=True)

    # Create timeline_events table
    op.create_table(
        'timeline_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('event_type', timeline_event_type_enum, nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('source_table', sa.String(50), nullable=True),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('scene_number', sa.Integer(), nullable=True),
        sa.Column('position_weight', sa.Float(), server_default='0.0'),
        sa.Column('start_chapter', sa.Integer(), nullable=True),
        sa.Column('end_chapter', sa.Integer(), nullable=True),
        sa.Column('duration_chapters', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layer', timeline_layer_enum, nullable=False, server_default='plot'),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('magnitude', sa.Float(), server_default='0.5'),
        sa.Column('is_major_beat', sa.Boolean(), server_default='false'),
        sa.Column('related_characters', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('related_locations', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('related_events', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), server_default='{}'),
        sa.Column('is_custom', sa.Boolean(), server_default='false'),
        sa.Column('is_visible', sa.Boolean(), server_default='true'),
        sa.Column('is_locked', sa.Boolean(), server_default='false'),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('sync_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timeline_events_project_id', 'timeline_events', ['project_id'])
    op.create_index('ix_timeline_events_event_type', 'timeline_events', ['event_type'])
    op.create_index('ix_timeline_events_chapter_number', 'timeline_events', ['chapter_number'])
    op.create_index('ix_timeline_events_layer', 'timeline_events', ['layer'])

    # Create timeline_conflicts table
    op.create_table(
        'timeline_conflicts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('conflict_type', conflict_type_enum, nullable=False),
        sa.Column('severity', conflict_severity_enum, nullable=False, server_default='warning'),
        sa.Column('chapter_start', sa.Integer(), nullable=True),
        sa.Column('chapter_end', sa.Integer(), nullable=True),
        sa.Column('event_ids', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('suggestions', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('status', sa.String(20), server_default='open'),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('detection_method', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timeline_conflicts_project_id', 'timeline_conflicts', ['project_id'])
    op.create_index('ix_timeline_conflicts_conflict_type', 'timeline_conflicts', ['conflict_type'])
    op.create_index('ix_timeline_conflicts_severity', 'timeline_conflicts', ['severity'])

    # Create timeline_views table
    op.create_table(
        'timeline_views',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), server_default='{}'),
        sa.Column('is_default', sa.Boolean(), server_default='false'),
        sa.Column('is_shared', sa.Boolean(), server_default='false'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('use_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timeline_views_project_id', 'timeline_views', ['project_id'])

    # Create timeline_bookmarks table
    op.create_table(
        'timeline_bookmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), server_default='#FFD700'),
        sa.Column('icon', sa.String(50), server_default='bookmark'),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timeline_bookmarks_project_id', 'timeline_bookmarks', ['project_id'])
    op.create_index('ix_timeline_bookmarks_user_id', 'timeline_bookmarks', ['user_id'])


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_timeline_bookmarks_user_id', table_name='timeline_bookmarks')
    op.drop_index('ix_timeline_bookmarks_project_id', table_name='timeline_bookmarks')
    op.drop_table('timeline_bookmarks')

    op.drop_index('ix_timeline_views_project_id', table_name='timeline_views')
    op.drop_table('timeline_views')

    op.drop_index('ix_timeline_conflicts_severity', table_name='timeline_conflicts')
    op.drop_index('ix_timeline_conflicts_conflict_type', table_name='timeline_conflicts')
    op.drop_index('ix_timeline_conflicts_project_id', table_name='timeline_conflicts')
    op.drop_table('timeline_conflicts')

    op.drop_index('ix_timeline_events_layer', table_name='timeline_events')
    op.drop_index('ix_timeline_events_chapter_number', table_name='timeline_events')
    op.drop_index('ix_timeline_events_event_type', table_name='timeline_events')
    op.drop_index('ix_timeline_events_project_id', table_name='timeline_events')
    op.drop_table('timeline_events')

    # Drop enums
    conflict_severity_enum = postgresql.ENUM(name='conflictseverity')
    conflict_severity_enum.drop(op.get_bind(), checkfirst=True)

    conflict_type_enum = postgresql.ENUM(name='conflicttype')
    conflict_type_enum.drop(op.get_bind(), checkfirst=True)

    timeline_layer_enum = postgresql.ENUM(name='timelinelayer')
    timeline_layer_enum.drop(op.get_bind(), checkfirst=True)

    timeline_event_type_enum = postgresql.ENUM(name='timelineeventtype')
    timeline_event_type_enum.drop(op.get_bind(), checkfirst=True)
