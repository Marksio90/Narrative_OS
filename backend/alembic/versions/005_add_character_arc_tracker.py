"""Add character arc tracker tables

Revision ID: 005
Revises: 004
Create Date: 2026-01-10

Character Arc Tracker feature:
- character_arcs: Overall character development arcs
- arc_milestones: Key moments in character development
- emotional_states: Emotional journey tracking per chapter
- goal_progress: Progress on character goals
- relationship_evolution: How relationships change over time
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create arc_type enum
    arc_type_enum = postgresql.ENUM(
        'positive_change', 'negative_change', 'flat_arc', 'transformation',
        'redemption', 'corruption', 'disillusionment', 'coming_of_age', 'tragic',
        name='arctype',
        create_type=True
    )
    arc_type_enum.create(op.get_bind(), checkfirst=True)

    # Create milestone_type enum
    milestone_type_enum = postgresql.ENUM(
        'catalyst', 'first_challenge', 'crisis', 'revelation', 'turning_point',
        'dark_night', 'breakthrough', 'climax', 'resolution', 'aftermath',
        name='milestonetype',
        create_type=True
    )
    milestone_type_enum.create(op.get_bind(), checkfirst=True)

    # Create goal_status enum
    goal_status_enum = postgresql.ENUM(
        'not_started', 'active', 'in_progress', 'blocked',
        'achieved', 'failed', 'abandoned',
        name='goalstatus',
        create_type=True
    )
    goal_status_enum.create(op.get_bind(), checkfirst=True)

    # === Create character_arcs table ===
    op.create_table(
        'character_arcs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),

        # Arc Definition
        sa.Column('arc_type', arc_type_enum, nullable=False),
        sa.Column('name', sa.String(255), nullable=True, comment="Arc name"),
        sa.Column('description', sa.Text(), nullable=True, comment="What this arc is about"),

        # Start/End States
        sa.Column('starting_state', postgresql.JSONB, nullable=False, server_default='{}', comment="""
            {
                'emotional': str,
                'beliefs': [str],
                'skills': [str],
                'relationships': {}
            }
        """),
        sa.Column('ending_state', postgresql.JSONB, nullable=False, server_default='{}', comment="""
            Target end state
        """),

        # Progress Tracking
        sa.Column('start_chapter', sa.Integer(), nullable=True),
        sa.Column('end_chapter', sa.Integer(), nullable=True),
        sa.Column('current_chapter', sa.Integer(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=False, server_default='0.0'),

        # Arc Health
        sa.Column('is_on_track', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('pacing_score', sa.Float(), nullable=True),
        sa.Column('consistency_score', sa.Float(), nullable=True),

        # Validation
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('validation_notes', postgresql.JSONB, nullable=False, server_default='[]'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_character_arcs_project_id', 'character_arcs', ['project_id'])
    op.create_index('ix_character_arcs_character_id', 'character_arcs', ['character_id'])

    # === Create arc_milestones table ===
    op.create_table(
        'arc_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('arc_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),

        # When/Where
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True),
        sa.Column('story_event_id', sa.Integer(), nullable=True, comment="Link to Consequence Simulator"),

        # Milestone Details
        sa.Column('milestone_type', milestone_type_enum, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # Impact
        sa.Column('emotional_impact', sa.Float(), nullable=True, comment="0-1"),
        sa.Column('character_change', sa.Text(), nullable=True),
        sa.Column('significance', sa.Float(), nullable=False, server_default='0.5'),

        # Progress
        sa.Column('is_achieved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expected_chapter', sa.Integer(), nullable=True),
        sa.Column('actual_chapter', sa.Integer(), nullable=True),

        # AI Analysis
        sa.Column('ai_analysis', postgresql.JSONB, nullable=False, server_default='{}'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['arc_id'], ['character_arcs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['story_event_id'], ['story_events.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_arc_milestones_arc_id', 'arc_milestones', ['arc_id'])
    op.create_index('ix_arc_milestones_project_id', 'arc_milestones', ['project_id'])
    op.create_index('ix_arc_milestones_chapter_number', 'arc_milestones', ['chapter_number'])

    # === Create emotional_states table ===
    op.create_table(
        'emotional_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('character_arc_id', sa.Integer(), nullable=True),
        sa.Column('chapter_number', sa.Integer(), nullable=False),

        # Emotional Data
        sa.Column('dominant_emotion', sa.String(100), nullable=True),
        sa.Column('secondary_emotions', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('intensity', sa.Float(), nullable=True, comment="0-1"),
        sa.Column('valence', sa.Float(), nullable=True, comment="-1 to 1"),

        # Context
        sa.Column('triggers', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('inner_conflict', sa.Text(), nullable=True),

        # Physical/Mental State
        sa.Column('mental_state', sa.String(100), nullable=True),
        sa.Column('stress_level', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),

        # AI Detection
        sa.Column('detected_from_text', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('source_scene_id', sa.Integer(), nullable=True),
        sa.Column('ai_confidence', sa.Float(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_arc_id'], ['character_arcs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_scene_id'], ['scenes.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_emotional_states_project_id', 'emotional_states', ['project_id'])
    op.create_index('ix_emotional_states_character_id', 'emotional_states', ['character_id'])
    op.create_index('ix_emotional_states_chapter_number', 'emotional_states', ['chapter_number'])

    # === Create goal_progress table ===
    op.create_table(
        'goal_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('character_arc_id', sa.Integer(), nullable=True),

        # Goal Identity
        sa.Column('goal_description', sa.Text(), nullable=False),
        sa.Column('goal_type', sa.String(100), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),

        # Tracking
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', goal_status_enum, nullable=False, server_default='active'),

        # Journey
        sa.Column('obstacles_faced', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('victories', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('setbacks', postgresql.JSONB, nullable=False, server_default='[]'),

        # Motivation
        sa.Column('motivation_strength', sa.Float(), nullable=True),
        sa.Column('stakes', sa.Text(), nullable=True),

        # Resolution
        sa.Column('achieved_chapter', sa.Integer(), nullable=True),
        sa.Column('failed_chapter', sa.Integer(), nullable=True),
        sa.Column('abandonment_reason', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_arc_id'], ['character_arcs.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_goal_progress_project_id', 'goal_progress', ['project_id'])
    op.create_index('ix_goal_progress_character_id', 'goal_progress', ['character_id'])
    op.create_index('ix_goal_progress_chapter_number', 'goal_progress', ['chapter_number'])

    # === Create relationship_evolution table ===
    op.create_table(
        'relationship_evolution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('related_character_id', sa.Integer(), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),

        # Relationship State
        sa.Column('relationship_type', sa.String(100), nullable=True),
        sa.Column('trust_level', sa.Float(), nullable=True),
        sa.Column('affection_level', sa.Float(), nullable=True),
        sa.Column('respect_level', sa.Float(), nullable=True),
        sa.Column('conflict_level', sa.Float(), nullable=True),

        # Overall Strength
        sa.Column('relationship_strength', sa.Float(), nullable=True, comment="-1 to 1"),

        # Changes
        sa.Column('key_moments', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('current_status', sa.Text(), nullable=True),
        sa.Column('trajectory', sa.String(50), nullable=True),

        # Context
        sa.Column('last_interaction_chapter', sa.Integer(), nullable=True),
        sa.Column('last_interaction_type', sa.String(100), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_character_id'], ['characters.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_relationship_evolution_project_id', 'relationship_evolution', ['project_id'])
    op.create_index('ix_relationship_evolution_character_id', 'relationship_evolution', ['character_id'])
    op.create_index('ix_relationship_evolution_chapter_number', 'relationship_evolution', ['chapter_number'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('relationship_evolution')
    op.drop_table('goal_progress')
    op.drop_table('emotional_states')
    op.drop_table('arc_milestones')
    op.drop_table('character_arcs')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS arctype')
    op.execute('DROP TYPE IF EXISTS milestonetype')
    op.execute('DROP TYPE IF EXISTS goalstatus')
