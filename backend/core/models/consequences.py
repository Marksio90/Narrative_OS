"""
Consequence Simulator Models

Tracks story events and their ripple effects through the narrative
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import Base, TimestampMixin


class EventType(enum.Enum):
    """Types of story events"""
    DECISION = "decision"
    REVELATION = "revelation"
    CONFLICT = "conflict"
    RESOLUTION = "resolution"
    DISCOVERY = "discovery"
    LOSS = "loss"
    TRANSFORMATION = "transformation"
    OTHER = "other"


class ConsequenceStatus(enum.Enum):
    """Status of a consequence"""
    POTENTIAL = "potential"  # Predicted but not yet realized
    ACTIVE = "active"  # In progress/ongoing
    REALIZED = "realized"  # Actually occurred
    INVALIDATED = "invalidated"  # No longer possible


class ConsequenceTimeframe(enum.Enum):
    """When a consequence occurs"""
    IMMEDIATE = "immediate"  # Same scene/chapter
    SHORT_TERM = "short_term"  # Next few chapters
    LONG_TERM = "long_term"  # Many chapters later


class StoryEvent(Base, TimestampMixin):
    """
    A significant event or decision in the story

    Events are extracted from scenes and tracked for their
    consequences and causal relationships.
    """
    __tablename__ = "story_events"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    scene_id = Column(Integer, nullable=True, comment="Scene where event occurs")
    chapter_number = Column(Integer, nullable=True, index=True)

    # Event details
    title = Column(String(255), nullable=False, comment="Brief event title")
    description = Column(Text, nullable=False, comment="Detailed event description")
    event_type = Column(Enum(EventType), nullable=False)

    # Impact
    magnitude = Column(Float, nullable=False, default=0.5, comment="Impact magnitude 0-1")
    emotional_impact = Column(Float, nullable=True, comment="Emotional weight 0-1")

    # Causality (stored as lists of event IDs)
    causes = Column(JSON, nullable=False, default=list, comment="Event IDs that caused this")
    effects = Column(JSON, nullable=False, default=list, comment="Event IDs caused by this")

    # AI-generated insights
    ai_analysis = Column(JSON, nullable=True, comment="""
        {
            'key_details': [str],
            'story_significance': str,
            'character_implications': {character_id: str},
            'plot_thread_impact': {thread_id: str}
        }
    """)

    # Metadata
    extracted_at = Column(DateTime, nullable=True, comment="When AI extracted this event")

    # Relationships
    consequences_caused = relationship(
        "Consequence",
        foreign_keys="Consequence.source_event_id",
        back_populates="source_event",
        cascade="all, delete-orphan"
    )
    consequences_realized = relationship(
        "Consequence",
        foreign_keys="Consequence.target_event_id",
        back_populates="target_event"
    )
    entity_relationships = relationship(
        "EventEntity",
        back_populates="event",
        cascade="all, delete-orphan"
    )


class Consequence(Base, TimestampMixin):
    """
    A predicted or realized consequence of a story event

    Tracks how events ripple through the narrative and affect
    characters, locations, and plot threads.
    """
    __tablename__ = "consequences"

    id = Column(Integer, primary_key=True, index=True)
    source_event_id = Column(
        Integer,
        ForeignKey("story_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Event that causes this consequence"
    )
    target_event_id = Column(
        Integer,
        ForeignKey("story_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Event where consequence is realized"
    )

    # Consequence details
    description = Column(Text, nullable=False, comment="What happens as a consequence")
    probability = Column(Float, nullable=False, default=0.5, comment="Likelihood 0-1")
    timeframe = Column(Enum(ConsequenceTimeframe), nullable=False, default=ConsequenceTimeframe.SHORT_TERM)
    status = Column(
        Enum(ConsequenceStatus),
        nullable=False,
        default=ConsequenceStatus.POTENTIAL,
        index=True
    )

    # Affected entities
    affected_entities = Column(JSON, nullable=False, default=dict, comment="""
        {
            'character_ids': [int],
            'location_ids': [int],
            'thread_ids': [int]
        }
    """)

    # Impact assessment
    severity = Column(Float, nullable=False, default=0.5, comment="Impact severity 0-1")
    plot_impact = Column(String(50), nullable=True, comment="major, moderate, minor")

    # AI predictions
    ai_prediction = Column(JSON, nullable=True, comment="""
        {
            'reasoning': str,
            'alternative_outcomes': [str],
            'mitigation_strategies': [str],
            'narrative_potential': str
        }
    """)

    # Tracking
    predicted_at = Column(DateTime, nullable=True, comment="When AI predicted this")
    realized_at = Column(DateTime, nullable=True, comment="When consequence actually occurred")
    invalidated_at = Column(DateTime, nullable=True, comment="When consequence became impossible")
    invalidation_reason = Column(Text, nullable=True)

    # Relationships
    source_event = relationship(
        "StoryEvent",
        foreign_keys=[source_event_id],
        back_populates="consequences_caused"
    )
    target_event = relationship(
        "StoryEvent",
        foreign_keys=[target_event_id],
        back_populates="consequences_realized"
    )


class EventEntity(Base):
    """
    Junction table linking events to canon entities

    Tracks which characters, locations, and threads are involved
    in each event.
    """
    __tablename__ = "event_entities"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("story_events.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True, comment="character, location, thread")
    entity_id = Column(Integer, nullable=False, index=True, comment="ID of the entity")
    involvement_type = Column(String(50), nullable=True, comment="protagonist, affected, witness, etc.")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    event = relationship("StoryEvent", back_populates="entity_relationships")
