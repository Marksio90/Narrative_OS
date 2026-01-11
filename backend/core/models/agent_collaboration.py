"""
Agent Collaboration System Models

Multi-agent AI collaboration for writing projects:
- Agent: AI agents with specialized roles (plotting, character, dialogue, etc.)
- AgentTask: Tasks delegated to agents
- AgentConversation: Multi-agent discussions
- AgentMessage: Messages in agent conversations
- AgentMemory: Persistent agent knowledge and learning
- AgentVote: Voting on conflicting suggestions
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import Optional, Dict, Any, List

from backend.core.database import Base
from backend.core.models.mixins import TimestampMixin


# ==================== ENUMS ====================

class AgentType(str, enum.Enum):
    """Type of AI agent"""
    PLOTTING = "plotting"           # Story structure and plot development
    CHARACTER = "character"         # Character development and arcs
    DIALOGUE = "dialogue"           # Dialogue writing and refinement
    CONTINUITY = "continuity"       # Consistency and continuity checking
    QC = "qc"                      # Quality control and review
    PACING = "pacing"              # Story pacing analysis
    THEME = "theme"                # Thematic development
    WORLDBUILDING = "worldbuilding" # World consistency
    CUSTOM = "custom"              # User-defined agent


class AgentRole(str, enum.Enum):
    """Agent role in collaboration"""
    LEADER = "leader"              # Leads the workflow
    CONTRIBUTOR = "contributor"    # Provides suggestions
    REVIEWER = "reviewer"          # Reviews and validates
    OBSERVER = "observer"          # Monitors but doesn't act


class TaskStatus(str, enum.Enum):
    """Status of agent task"""
    PENDING = "pending"            # Waiting to be picked up
    ASSIGNED = "assigned"          # Assigned to agent
    IN_PROGRESS = "in_progress"    # Agent is working on it
    COMPLETED = "completed"        # Task finished
    FAILED = "failed"              # Task failed
    CANCELLED = "cancelled"        # Task cancelled
    BLOCKED = "blocked"            # Blocked by dependencies


class TaskPriority(str, enum.Enum):
    """Priority level for tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConflictResolutionStrategy(str, enum.Enum):
    """How to resolve conflicting suggestions"""
    VOTING = "voting"              # Agents vote on best option
    HIERARCHY = "hierarchy"        # Use agent role hierarchy
    USER_CHOICE = "user_choice"    # Let user decide
    CONSENSUS = "consensus"        # Require all agents to agree
    AI_JUDGE = "ai_judge"          # Use separate AI to judge


class MemoryType(str, enum.Enum):
    """Type of agent memory"""
    EPISODIC = "episodic"          # Specific events/interactions
    SEMANTIC = "semantic"          # General knowledge
    PROCEDURAL = "procedural"      # How-to knowledge
    FEEDBACK = "feedback"          # User feedback learning


# ==================== MODELS ====================

class Agent(Base, TimestampMixin):
    """
    AI Agent configuration and state

    Represents an AI agent with specialized capabilities.
    Each agent has a type (plotting, character, etc.) and can be
    configured with custom prompts, model preferences, and memory.
    """
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Agent identity
    name = Column(String(200), nullable=False)  # e.g., "Plot Master", "Character Dev"
    agent_type = Column(SQLEnum(AgentType), nullable=False, index=True)
    role = Column(SQLEnum(AgentRole), nullable=False, default=AgentRole.CONTRIBUTOR)

    # Agent configuration
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)  # Custom system prompt
    model_name = Column(String(100), default="claude-sonnet-4")  # AI model to use
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)

    # Agent capabilities
    capabilities = Column(JSON, default=list)  # List of specific skills
    """
    Example capabilities:
    ["plot_analysis", "character_motivation", "dialogue_writing",
     "continuity_checking", "pacing_analysis"]
    """

    # Agent state
    is_active = Column(Boolean, default=True)
    is_busy = Column(Boolean, default=False)  # Currently working on task
    current_task_id = Column(Integer, ForeignKey("agent_tasks.id"), nullable=True)

    # Performance tracking
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    average_completion_time = Column(Float, nullable=True)  # seconds
    user_satisfaction_score = Column(Float, nullable=True)  # 0-1

    # Memory settings
    enable_memory = Column(Boolean, default=True)
    memory_window = Column(Integer, default=10)  # How many past interactions to remember

    # Metadata
    config = Column(JSON, default=dict)
    """
    Additional configuration:
    {
        "auto_delegate": true,
        "conflict_behavior": "defer_to_user",
        "notification_preferences": {...},
        "rate_limit": 100  # tasks per day
    }
    """

    # Relationships
    tasks = relationship("AgentTask", back_populates="agent", foreign_keys="AgentTask.agent_id")
    messages = relationship("AgentMessage", back_populates="agent")
    memories = relationship("AgentMemory", back_populates="agent", cascade="all, delete-orphan")
    votes = relationship("AgentVote", back_populates="agent")

    def __repr__(self):
        return f"<Agent {self.name} ({self.agent_type})>"


class AgentTask(Base, TimestampMixin):
    """
    Task assigned to an agent

    Represents a unit of work for an agent. Tasks can have dependencies,
    priorities, and can be part of larger workflows.
    """
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)

    # Task definition
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(String(100), nullable=True)  # "analyze_plot", "develop_character", etc.

    # Task status
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    priority = Column(SQLEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM, index=True)

    # Task context
    context = Column(JSON, default=dict)
    """
    Context for the task:
    {
        "chapter_id": 123,
        "character_ids": [1, 2, 3],
        "related_events": [...],
        "user_instructions": "Focus on emotional beats"
    }
    """

    # Task dependencies
    depends_on = Column(JSON, default=list)  # List of task IDs that must complete first
    blocks_tasks = Column(JSON, default=list)  # List of task IDs that depend on this

    # Execution tracking
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)

    # Results
    result = Column(JSON, nullable=True)
    """
    Task result:
    {
        "suggestions": [...],
        "changes_made": [...],
        "analysis": {...},
        "confidence": 0.85,
        "requires_review": false
    }
    """

    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # User feedback
    user_approved = Column(Boolean, nullable=True)
    user_feedback = Column(Text, nullable=True)
    user_rating = Column(Float, nullable=True)  # 0-5 stars

    # Metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    task_metadata = Column(JSON, default=dict)

    # Relationships
    agent = relationship("Agent", back_populates="tasks", foreign_keys=[agent_id])

    def __repr__(self):
        return f"<AgentTask {self.title} ({self.status})>"

    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies"""
        # Would need to query database to check if depends_on tasks are completed
        return self.status == TaskStatus.BLOCKED

    @property
    def completion_time(self) -> Optional[float]:
        """Get task completion time in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class AgentConversation(Base, TimestampMixin):
    """
    Multi-agent discussion thread

    Agents can discuss and collaborate on complex tasks.
    Conversations allow agents to share insights, debate options,
    and reach consensus.
    """
    __tablename__ = "agent_conversations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Conversation metadata
    title = Column(String(500), nullable=False)
    topic = Column(String(200), nullable=True)  # "plot_conflict", "character_motivation", etc.

    # Participants
    participant_agent_ids = Column(JSON, default=list)  # List of agent IDs
    moderator_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)

    # Conversation state
    is_active = Column(Boolean, default=True)
    is_resolved = Column(Boolean, default=False)
    resolution_summary = Column(Text, nullable=True)

    # Related entities
    related_task_id = Column(Integer, ForeignKey("agent_tasks.id"), nullable=True)
    related_chapter_id = Column(Integer, nullable=True)
    related_character_ids = Column(JSON, default=list)

    # Conflict resolution
    has_conflict = Column(Boolean, default=False)
    conflict_type = Column(String(100), nullable=True)
    resolution_strategy = Column(SQLEnum(ConflictResolutionStrategy), nullable=True)

    # Voting (if resolution strategy is VOTING)
    voting_options = Column(JSON, nullable=True)
    """
    Voting options:
    [
        {"id": 1, "description": "Option A", "proposed_by_agent_id": 1},
        {"id": 2, "description": "Option B", "proposed_by_agent_id": 2}
    ]
    """
    voting_deadline = Column(DateTime, nullable=True)
    winning_option_id = Column(Integer, nullable=True)

    # Metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    conversation_metadata = Column(JSON, default=dict)

    # Relationships
    messages = relationship("AgentMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AgentMessage.created_at")
    votes = relationship("AgentVote", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AgentConversation {self.title}>"


class AgentMessage(Base, TimestampMixin):
    """
    Message in agent conversation

    Individual messages from agents in a discussion thread.
    """
    __tablename__ = "agent_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("agent_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)

    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="comment")  # "comment", "suggestion", "question", "vote"

    # Message metadata
    is_suggestion = Column(Boolean, default=False)
    suggestion_data = Column(JSON, nullable=True)  # If message contains a suggestion

    # References
    reply_to_message_id = Column(Integer, ForeignKey("agent_messages.id"), nullable=True)
    mentioned_agent_ids = Column(JSON, default=list)

    # Reactions
    reactions = Column(JSON, default=dict)
    """
    Reactions from other agents:
    {
        "👍": [agent_id_1, agent_id_2],
        "🤔": [agent_id_3]
    }
    """

    # AI metadata
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)

    # Relationships
    conversation = relationship("AgentConversation", back_populates="messages")
    agent = relationship("Agent", back_populates="messages")

    def __repr__(self):
        return f"<AgentMessage from Agent {self.agent_id}>"


class AgentMemory(Base, TimestampMixin):
    """
    Persistent agent memory and knowledge

    Agents learn from interactions and store knowledge.
    Uses vector embeddings for semantic search.
    """
    __tablename__ = "agent_memories"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)

    # Memory type and content
    memory_type = Column(SQLEnum(MemoryType), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # Semantic search
    embedding = Column(JSON, nullable=True)  # Vector embedding for similarity search
    embedding_model = Column(String(100), default="text-embedding-3-small")

    # Memory metadata
    importance = Column(Float, default=0.5)  # 0-1, how important is this memory
    access_count = Column(Integer, default=0)  # How often accessed
    last_accessed_at = Column(DateTime, nullable=True)

    # Source information
    source_type = Column(String(100), nullable=True)  # "task", "conversation", "feedback"
    source_id = Column(Integer, nullable=True)  # ID of source entity

    # Context
    context = Column(JSON, default=dict)
    """
    Context for memory:
    {
        "chapter_range": [1, 5],
        "characters": [1, 2],
        "tags": ["plot", "motivation"],
        "user_feedback": "positive"
    }
    """

    # Memory decay (for episodic memories)
    decay_rate = Column(Float, default=0.1)  # How fast memory fades
    expires_at = Column(DateTime, nullable=True)  # When to auto-delete

    # Relationships
    agent = relationship("Agent", back_populates="memories")

    def __repr__(self):
        return f"<AgentMemory {self.memory_type} for Agent {self.agent_id}>"

    @property
    def is_expired(self) -> bool:
        """Check if memory has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class AgentVote(Base, TimestampMixin):
    """
    Agent vote on conflicting suggestions

    When agents have conflicting opinions, they can vote
    on the best option.
    """
    __tablename__ = "agent_votes"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("agent_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)

    # Vote
    option_id = Column(Integer, nullable=False)  # Which option agent voted for
    confidence = Column(Float, nullable=True)  # 0-1, how confident in this vote

    # Reasoning
    reasoning = Column(Text, nullable=True)  # Why agent voted this way

    # Vote metadata
    vote_weight = Column(Float, default=1.0)  # Some agents may have more weight
    is_final = Column(Boolean, default=True)  # Can agent change vote?

    # Relationships
    conversation = relationship("AgentConversation", back_populates="votes")
    agent = relationship("Agent", back_populates="votes")

    def __repr__(self):
        return f"<AgentVote Agent {self.agent_id} -> Option {self.option_id}>"


# ==================== INDEXES ====================

# Performance indexes for common queries
Index('ix_agent_tasks_project_status', AgentTask.project_id, AgentTask.status)
Index('ix_agent_tasks_agent_status', AgentTask.agent_id, AgentTask.status)
Index('ix_agent_conversations_project_active', AgentConversation.project_id, AgentConversation.is_active)
Index('ix_agent_memories_agent_type', AgentMemory.agent_id, AgentMemory.memory_type)
