"""Add consequence simulator tables

Revision ID: 004
Revises: 003
Create Date: 2026-01-09

Consequence Simulator feature:
- story_events: Significant story events and decisions
- consequences: Predicted/realized consequences of events
- event_entities: Relationships between events and canon entities
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create event_type enum
    event_type_enum = postgresql.ENUM(
        'decision', 'revelation', 'conflict', 'resolution',
        'discovery', 'loss', 'transformation', 'other',
        name='eventtype',
        create_type=True
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)

    # Create consequence_status enum
    consequence_status_enum = postgresql.ENUM(
        'potential', 'active', 'realized', 'invalidated',
        name='consequencestatus',
        create_type=True
    )
    consequence_status_enum.create(op.get_bind(), checkfirst=True)

    # Create consequence_timeframe enum
    consequence_timeframe_enum = postgresql.ENUM(
        'immediate', 'short_term', 'long_term',
        name='consequencetimeframe',
        create_type=True
    )
    consequence_timeframe_enum.create(op.get_bind(), checkfirst=True)

    # === Create story_events table ===
    op.create_table(
        'story_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True, comment="Scene where event occurs"),
        sa.Column('chapter_number', sa.Integer(), nullable=True, index=True),

        # Event details
        sa.Column('title', sa.String(255), nullable=False, comment="Brief event title"),
        sa.Column('description', sa.Text(), nullable=False, comment="Detailed event description"),
        sa.Column('event_type', event_type_enum, nullable=False),

        # Impact
        sa.Column('magnitude', sa.Float(), nullable=False, server_default='0.5', comment="Impact magnitude 0-1"),
        sa.Column('emotional_impact', sa.Float(), nullable=True, comment="Emotional weight 0-1"),

        # Causality
        sa.Column('causes', postgresql.JSONB, nullable=False, server_default='[]', comment="Event IDs that caused this"),
        sa.Column('effects', postgresql.JSONB, nullable=False, server_default='[]', comment="Event IDs caused by this"),

        # AI-generated insights
        sa.Column('ai_analysis', postgresql.JSONB, nullable=True, comment="""
            {
                'key_details': [str],
                'story_significance': str,
                'character_implications': {character_id: str},
                'plot_thread_impact': {thread_id: str}
            }
        """),

        # Metadata
        sa.Column('extracted_at', sa.DateTime(), nullable=True, comment="When AI extracted this event"),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )

    # Indexes for story_events
    op.create_index('ix_story_events_project_id', 'story_events', ['project_id'])
    op.create_index('ix_story_events_chapter_number', 'story_events', ['chapter_number'])
    op.create_index('ix_story_events_event_type', 'story_events', ['event_type'])
    op.create_index('ix_story_events_magnitude', 'story_events', ['magnitude'])

    # === Create consequences table ===
    op.create_table(
        'consequences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_event_id', sa.Integer(), nullable=False, comment="Event that causes this consequence"),
        sa.Column('target_event_id', sa.Integer(), nullable=True, comment="Event where consequence is realized"),

        # Consequence details
        sa.Column('description', sa.Text(), nullable=False, comment="What happens as a consequence"),
        sa.Column('probability', sa.Float(), nullable=False, server_default='0.5', comment="Likelihood 0-1"),
        sa.Column('timeframe', consequence_timeframe_enum, nullable=False, server_default='short_term'),
        sa.Column('status', consequence_status_enum, nullable=False, server_default='potential'),

        # Affected entities (stored as JSONB for flexibility)
        sa.Column('affected_entities', postgresql.JSONB, nullable=False, server_default='{}', comment="""
            {
                'character_ids': [int],
                'location_ids': [int],
                'thread_ids': [int]
            }
        """),

        # Impact assessment
        sa.Column('severity', sa.Float(), nullable=False, server_default='0.5', comment="Impact severity 0-1"),
        sa.Column('plot_impact', sa.String(50), nullable=True, comment="major, moderate, minor"),

        # AI predictions
        sa.Column('ai_prediction', postgresql.JSONB, nullable=True, comment="""
            {
                'reasoning': str,
                'alternative_outcomes': [str],
                'mitigation_strategies': [str],
                'narrative_potential': str
            }
        """),

        # Tracking
        sa.Column('predicted_at', sa.DateTime(), nullable=True, comment="When AI predicted this"),
        sa.Column('realized_at', sa.DateTime(), nullable=True, comment="When consequence actually occurred"),
        sa.Column('invalidated_at', sa.DateTime(), nullable=True, comment="When consequence became impossible"),
        sa.Column('invalidation_reason', sa.Text(), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_event_id'], ['story_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_event_id'], ['story_events.id'], ondelete='SET NULL'),
    )

    # Indexes for consequences
    op.create_index('ix_consequences_source_event_id', 'consequences', ['source_event_id'])
    op.create_index('ix_consequences_target_event_id', 'consequences', ['target_event_id'])
    op.create_index('ix_consequences_status', 'consequences', ['status'])
    op.create_index('ix_consequences_timeframe', 'consequences', ['timeframe'])
    op.create_index('ix_consequences_probability', 'consequences', ['probability'])

    # === Create event_entities junction table ===
    op.create_table(
        'event_entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False, comment="character, location, thread"),
        sa.Column('entity_id', sa.Integer(), nullable=False, comment="ID of the entity"),
        sa.Column('involvement_type', sa.String(50), nullable=True, comment="protagonist, affected, witness, etc."),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['story_events.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('event_id', 'entity_type', 'entity_id', name='uq_event_entity'),
    )

    # Indexes for event_entities
    op.create_index('ix_event_entities_event_id', 'event_entities', ['event_id'])
    op.create_index('ix_event_entities_entity_type', 'event_entities', ['entity_type'])
    op.create_index('ix_event_entities_entity_id', 'event_entities', ['entity_id'])
    op.create_index('ix_event_entities_composite', 'event_entities', ['entity_type', 'entity_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('event_entities')
    op.drop_table('consequences')
    op.drop_table('story_events')

    # Drop enums
    consequence_timeframe_enum = postgresql.ENUM(name='consequencetimeframe')
    consequence_timeframe_enum.drop(op.get_bind(), checkfirst=True)

    consequence_status_enum = postgresql.ENUM(name='consequencestatus')
    consequence_status_enum.drop(op.get_bind(), checkfirst=True)

    event_type_enum = postgresql.ENUM(name='eventtype')
    event_type_enum.drop(op.get_bind(), checkfirst=True)
