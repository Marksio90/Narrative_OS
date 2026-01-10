"""add agent collaboration

Revision ID: 007
Revises: 006
Create Date: 2026-01-10

Agent Collaboration System:
- agents: AI agents with specialized roles
- agent_tasks: Tasks delegated to agents
- agent_conversations: Multi-agent discussions
- agent_messages: Messages in conversations
- agent_memories: Persistent agent knowledge
- agent_votes: Voting on conflicting suggestions
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    agent_type_enum = postgresql.ENUM(
        'plotting', 'character', 'dialogue', 'continuity', 'qc',
        'pacing', 'theme', 'worldbuilding', 'custom',
        name='agenttype', create_type=True
    )

    agent_role_enum = postgresql.ENUM(
        'leader', 'contributor', 'reviewer', 'observer',
        name='agentrole', create_type=True
    )

    task_status_enum = postgresql.ENUM(
        'pending', 'assigned', 'in_progress', 'completed', 'failed', 'cancelled', 'blocked',
        name='taskstatus', create_type=True
    )

    task_priority_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='taskpriority', create_type=True
    )

    conflict_resolution_strategy_enum = postgresql.ENUM(
        'voting', 'hierarchy', 'user_choice', 'consensus', 'ai_judge',
        name='conflictresolutionstrategy', create_type=True
    )

    memory_type_enum = postgresql.ENUM(
        'episodic', 'semantic', 'procedural', 'feedback',
        name='memorytype', create_type=True
    )

    # ==================== CREATE TABLES ====================

    # 1. agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),

        # Agent identity
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('agent_type', agent_type_enum, nullable=False),
        sa.Column('role', agent_role_enum, nullable=False, server_default='contributor'),

        # Agent configuration
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('model_name', sa.String(100), nullable=True, server_default='claude-sonnet-4'),
        sa.Column('temperature', sa.Float(), nullable=True, server_default='0.7'),
        sa.Column('max_tokens', sa.Integer(), nullable=True, server_default='4000'),

        # Agent capabilities
        sa.Column('capabilities', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'),

        # Agent state
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_busy', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('current_task_id', sa.Integer(), nullable=True),

        # Performance tracking
        sa.Column('tasks_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tasks_failed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('average_completion_time', sa.Float(), nullable=True),
        sa.Column('user_satisfaction_score', sa.Float(), nullable=True),

        # Memory settings
        sa.Column('enable_memory', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('memory_window', sa.Integer(), nullable=True, server_default='10'),

        # Metadata
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. agent_tasks table
    op.create_table(
        'agent_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=True),

        # Task definition
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('task_type', sa.String(100), nullable=True),

        # Task status
        sa.Column('status', task_status_enum, nullable=False, server_default='pending'),
        sa.Column('priority', task_priority_enum, nullable=False, server_default='medium'),

        # Task context
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # Task dependencies
        sa.Column('depends_on', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('blocks_tasks', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'),

        # Execution tracking
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),

        # Results
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=True, server_default='3'),

        # User feedback
        sa.Column('user_approved', sa.Boolean(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('user_rating', sa.Float(), nullable=True),

        # Metadata
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. agent_conversations table
    op.create_table(
        'agent_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),

        # Conversation metadata
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('topic', sa.String(200), nullable=True),

        # Participants
        sa.Column('participant_agent_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('moderator_agent_id', sa.Integer(), nullable=True),

        # Conversation state
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_resolved', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('resolution_summary', sa.Text(), nullable=True),

        # Related entities
        sa.Column('related_task_id', sa.Integer(), nullable=True),
        sa.Column('related_chapter_id', sa.Integer(), nullable=True),
        sa.Column('related_character_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'),

        # Conflict resolution
        sa.Column('has_conflict', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('conflict_type', sa.String(100), nullable=True),
        sa.Column('resolution_strategy', conflict_resolution_strategy_enum, nullable=True),

        # Voting
        sa.Column('voting_options', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('voting_deadline', sa.DateTime(), nullable=True),
        sa.Column('winning_option_id', sa.Integer(), nullable=True),

        # Metadata
        sa.Column('started_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['moderator_agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_task_id'], ['agent_tasks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. agent_messages table
    op.create_table(
        'agent_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=True),

        # Message content
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(50), nullable=True, server_default='comment'),

        # Message metadata
        sa.Column('is_suggestion', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('suggestion_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # References
        sa.Column('reply_to_message_id', sa.Integer(), nullable=True),
        sa.Column('mentioned_agent_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'),

        # Reactions
        sa.Column('reactions', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # AI metadata
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['conversation_id'], ['agent_conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reply_to_message_id'], ['agent_messages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. agent_memories table
    op.create_table(
        'agent_memories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),

        # Memory type and content
        sa.Column('memory_type', memory_type_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),

        # Semantic search
        sa.Column('embedding', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('embedding_model', sa.String(100), nullable=True, server_default='text-embedding-3-small'),

        # Memory metadata
        sa.Column('importance', sa.Float(), nullable=True, server_default='0.5'),
        sa.Column('access_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),

        # Source information
        sa.Column('source_type', sa.String(100), nullable=True),
        sa.Column('source_id', sa.Integer(), nullable=True),

        # Context
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # Memory decay
        sa.Column('decay_rate', sa.Float(), nullable=True, server_default='0.1'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. agent_votes table
    op.create_table(
        'agent_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),

        # Vote
        sa.Column('option_id', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),

        # Reasoning
        sa.Column('reasoning', sa.Text(), nullable=True),

        # Vote metadata
        sa.Column('vote_weight', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('is_final', sa.Boolean(), nullable=True, server_default='true'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['conversation_id'], ['agent_conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ==================== CREATE INDEXES ====================

    # agents indexes
    op.create_index('ix_agents_id', 'agents', ['id'])
    op.create_index('ix_agents_project_id', 'agents', ['project_id'])
    op.create_index('ix_agents_agent_type', 'agents', ['agent_type'])

    # agent_tasks indexes
    op.create_index('ix_agent_tasks_id', 'agent_tasks', ['id'])
    op.create_index('ix_agent_tasks_project_id', 'agent_tasks', ['project_id'])
    op.create_index('ix_agent_tasks_agent_id', 'agent_tasks', ['agent_id'])
    op.create_index('ix_agent_tasks_status', 'agent_tasks', ['status'])
    op.create_index('ix_agent_tasks_priority', 'agent_tasks', ['priority'])
    op.create_index('ix_agent_tasks_project_status', 'agent_tasks', ['project_id', 'status'])
    op.create_index('ix_agent_tasks_agent_status', 'agent_tasks', ['agent_id', 'status'])

    # agent_conversations indexes
    op.create_index('ix_agent_conversations_id', 'agent_conversations', ['id'])
    op.create_index('ix_agent_conversations_project_id', 'agent_conversations', ['project_id'])
    op.create_index('ix_agent_conversations_project_active', 'agent_conversations', ['project_id', 'is_active'])

    # agent_messages indexes
    op.create_index('ix_agent_messages_id', 'agent_messages', ['id'])
    op.create_index('ix_agent_messages_conversation_id', 'agent_messages', ['conversation_id'])
    op.create_index('ix_agent_messages_agent_id', 'agent_messages', ['agent_id'])

    # agent_memories indexes
    op.create_index('ix_agent_memories_id', 'agent_memories', ['id'])
    op.create_index('ix_agent_memories_project_id', 'agent_memories', ['project_id'])
    op.create_index('ix_agent_memories_agent_id', 'agent_memories', ['agent_id'])
    op.create_index('ix_agent_memories_memory_type', 'agent_memories', ['memory_type'])
    op.create_index('ix_agent_memories_agent_type', 'agent_memories', ['agent_id', 'memory_type'])

    # agent_votes indexes
    op.create_index('ix_agent_votes_id', 'agent_votes', ['id'])
    op.create_index('ix_agent_votes_conversation_id', 'agent_votes', ['conversation_id'])
    op.create_index('ix_agent_votes_agent_id', 'agent_votes', ['agent_id'])

    # Add foreign key constraint for agents.current_task_id
    # (must be added after agent_tasks table exists)
    op.create_foreign_key(
        'fk_agents_current_task_id',
        'agents', 'agent_tasks',
        ['current_task_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key constraint first
    op.drop_constraint('fk_agents_current_task_id', 'agents', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_agent_votes_agent_id', 'agent_votes')
    op.drop_index('ix_agent_votes_conversation_id', 'agent_votes')
    op.drop_index('ix_agent_votes_id', 'agent_votes')

    op.drop_index('ix_agent_memories_agent_type', 'agent_memories')
    op.drop_index('ix_agent_memories_memory_type', 'agent_memories')
    op.drop_index('ix_agent_memories_agent_id', 'agent_memories')
    op.drop_index('ix_agent_memories_project_id', 'agent_memories')
    op.drop_index('ix_agent_memories_id', 'agent_memories')

    op.drop_index('ix_agent_messages_agent_id', 'agent_messages')
    op.drop_index('ix_agent_messages_conversation_id', 'agent_messages')
    op.drop_index('ix_agent_messages_id', 'agent_messages')

    op.drop_index('ix_agent_conversations_project_active', 'agent_conversations')
    op.drop_index('ix_agent_conversations_project_id', 'agent_conversations')
    op.drop_index('ix_agent_conversations_id', 'agent_conversations')

    op.drop_index('ix_agent_tasks_agent_status', 'agent_tasks')
    op.drop_index('ix_agent_tasks_project_status', 'agent_tasks')
    op.drop_index('ix_agent_tasks_priority', 'agent_tasks')
    op.drop_index('ix_agent_tasks_status', 'agent_tasks')
    op.drop_index('ix_agent_tasks_agent_id', 'agent_tasks')
    op.drop_index('ix_agent_tasks_project_id', 'agent_tasks')
    op.drop_index('ix_agent_tasks_id', 'agent_tasks')

    op.drop_index('ix_agents_agent_type', 'agents')
    op.drop_index('ix_agents_project_id', 'agents')
    op.drop_index('ix_agents_id', 'agents')

    # Drop tables
    op.drop_table('agent_votes')
    op.drop_table('agent_memories')
    op.drop_table('agent_messages')
    op.drop_table('agent_conversations')
    op.drop_table('agent_tasks')
    op.drop_table('agents')

    # Drop enums
    sa.Enum(name='memorytype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='conflictresolutionstrategy').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='taskpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='taskstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='agentrole').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='agenttype').drop(op.get_bind(), checkfirst=True)
