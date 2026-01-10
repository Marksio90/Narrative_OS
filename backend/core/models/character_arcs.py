"""
Character Arc Tracking Models

Track character development, emotional journeys, goal progress, and relationship evolution
across the narrative timeline.
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Float, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import Base, TimestampMixin


class ArcType(enum.Enum):
    """Types of character arcs"""
    POSITIVE_CHANGE = "positive_change"      # Character grows/improves
    NEGATIVE_CHANGE = "negative_change"      # Character corrupts/degrades
    FLAT_ARC = "flat_arc"                    # Character stays same, changes world
    TRANSFORMATION = "transformation"         # Complete character transformation
    REDEMPTION = "redemption"                 # Fall and rise
    CORRUPTION = "corruption"                 # Rise and fall
    DISILLUSIONMENT = "disillusionment"      # Loss of innocence/ideals
    COMING_OF_AGE = "coming_of_age"          # Maturation arc
    TRAGIC = "tragic"                         # Doomed trajectory


class MilestoneType(enum.Enum):
    """Key points in character development"""
    CATALYST = "catalyst"                     # Event that starts the arc
    FIRST_CHALLENGE = "first_challenge"       # Initial test
    CRISIS = "crisis"                         # Major conflict point
    REVELATION = "revelation"                 # Character realizes something
    TURNING_POINT = "turning_point"           # Point of no return
    DARK_NIGHT = "dark_night"                 # Lowest point
    BREAKTHROUGH = "breakthrough"             # Overcomes major obstacle
    CLIMAX = "climax"                         # Arc peak moment
    RESOLUTION = "resolution"                 # Arc concludes
    AFTERMATH = "aftermath"                   # New normal


class GoalStatus(enum.Enum):
    """Status of character goals"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    ACHIEVED = "achieved"
    FAILED = "failed"
    ABANDONED = "abandoned"


class CharacterArc(Base, TimestampMixin):
    """
    Main character arc tracking
    Represents the overall journey of a character through the story
    """
    __tablename__ = "character_arcs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)

    # Arc Definition
    arc_type = Column(Enum(ArcType), nullable=False)
    name = Column(String(255), comment="Arc name (e.g., 'Sarah's Journey to Trust')")
    description = Column(Text, comment="What this arc is about")

    # Start/End States
    starting_state = Column(JSON, default=dict, comment="""
        {
            'emotional': 'fearful',
            'beliefs': ['I can't trust anyone'],
            'skills': ['basic investigation'],
            'relationships': {...}
        }
    """)

    ending_state = Column(JSON, default=dict, comment="""
        Target end state - what character should become
    """)

    # Progress Tracking
    start_chapter = Column(Integer, comment="Chapter where arc begins")
    end_chapter = Column(Integer, comment="Target chapter where arc should complete")
    current_chapter = Column(Integer, comment="Last tracked chapter")
    completion_percentage = Column(Float, default=0.0, comment="0-100%")

    # Arc Health
    is_on_track = Column(Boolean, default=True, comment="Is arc progressing as planned?")
    pacing_score = Column(Float, comment="0-1, how well-paced is the development")
    consistency_score = Column(Float, comment="0-1, how consistent is character behavior")

    # Validation
    is_complete = Column(Boolean, default=False)
    validation_notes = Column(JSON, default=list, comment="Issues found by validation")

    # Relationships
    milestones = relationship("ArcMilestone", back_populates="arc", cascade="all, delete-orphan")
    emotional_states = relationship("EmotionalState", back_populates="character_arc")


class ArcMilestone(Base, TimestampMixin):
    """
    Key moments in character development
    Specific events that mark progress in the arc
    """
    __tablename__ = "arc_milestones"

    id = Column(Integer, primary_key=True, index=True)
    arc_id = Column(Integer, ForeignKey("character_arcs.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # When/Where
    chapter_number = Column(Integer, nullable=False, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)
    story_event_id = Column(Integer, ForeignKey("story_events.id"), nullable=True, comment="Link to Consequence Simulator")

    # Milestone Details
    milestone_type = Column(Enum(MilestoneType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Impact
    emotional_impact = Column(Float, comment="0-1, how strong was the impact")
    character_change = Column(Text, comment="What changed in the character")
    significance = Column(Float, default=0.5, comment="0-1, importance to overall arc")

    # Progress
    is_achieved = Column(Boolean, default=False, comment="Has this milestone been written?")
    expected_chapter = Column(Integer, comment="When was this milestone planned for?")
    actual_chapter = Column(Integer, comment="When did it actually happen?")

    # AI Analysis
    ai_analysis = Column(JSON, default=dict, comment="""
        {
            'detected_change': 'Character showed more trust',
            'consistency_score': 0.85,
            'suggestions': ['Deepen emotional reaction']
        }
    """)

    # Relationships
    arc = relationship("CharacterArc", back_populates="milestones")


class EmotionalState(Base, TimestampMixin):
    """
    Track character's emotional state per chapter
    Enables emotional journey visualization
    """
    __tablename__ = "emotional_states"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    character_arc_id = Column(Integer, ForeignKey("character_arcs.id"), nullable=True)
    chapter_number = Column(Integer, nullable=False, index=True)

    # Emotional Data
    dominant_emotion = Column(String(100), comment="Primary emotion (fear, anger, joy, etc.)")
    secondary_emotions = Column(JSON, default=list, comment="['hope', 'confusion']")
    intensity = Column(Float, comment="0-1, how intense is the emotion")
    valence = Column(Float, comment="-1 to 1, negative to positive")

    # Context
    triggers = Column(JSON, default=list, comment="""
        [
            {'event': 'Betrayal', 'impact': 0.9},
            {'event': 'Lost evidence', 'impact': 0.6}
        ]
    """)

    inner_conflict = Column(Text, comment="Internal struggle at this point")

    # Physical/Mental State
    mental_state = Column(String(100), comment="clarity, confusion, determination, etc.")
    stress_level = Column(Float, comment="0-1")
    confidence_level = Column(Float, comment="0-1")

    # AI Detection
    detected_from_text = Column(Boolean, default=False, comment="Was this AI-extracted from prose?")
    source_scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)
    ai_confidence = Column(Float, comment="0-1, confidence in AI detection")

    # Relationships
    character_arc = relationship("CharacterArc", back_populates="emotional_states")


class GoalProgress(Base, TimestampMixin):
    """
    Track progress on character goals across chapters
    Links to character.goals from canon
    """
    __tablename__ = "goal_progress"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    character_arc_id = Column(Integer, ForeignKey("character_arcs.id"), nullable=True)

    # Goal Identity
    goal_description = Column(Text, nullable=False, comment="What the character wants")
    goal_type = Column(String(100), comment="external, internal, relationship, etc.")
    priority = Column(Integer, default=1, comment="1=highest priority")

    # Tracking
    chapter_number = Column(Integer, nullable=False, index=True)
    progress_percentage = Column(Float, default=0.0, comment="0-100%")
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)

    # Journey
    obstacles_faced = Column(JSON, default=list, comment="""
        [
            {'chapter': 3, 'obstacle': 'Lost key witness', 'severity': 0.8},
            {'chapter': 5, 'obstacle': 'Betrayed by partner', 'severity': 0.9}
        ]
    """)

    victories = Column(JSON, default=list, comment="""
        Small wins along the way
    """)

    setbacks = Column(JSON, default=list, comment="""
        Major setbacks
    """)

    # Motivation
    motivation_strength = Column(Float, comment="0-1, how motivated is character?")
    stakes = Column(Text, comment="What happens if they fail?")

    # Resolution
    achieved_chapter = Column(Integer, nullable=True)
    failed_chapter = Column(Integer, nullable=True)
    abandonment_reason = Column(Text, nullable=True)


class RelationshipEvolution(Base, TimestampMixin):
    """
    Track how relationships change over time
    Complements Character.relationships with temporal data
    """
    __tablename__ = "relationship_evolution"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    related_character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False, index=True)

    # Relationship State
    relationship_type = Column(String(100), comment="friend, enemy, lover, mentor, etc.")
    trust_level = Column(Float, comment="0-1")
    affection_level = Column(Float, comment="0-1")
    respect_level = Column(Float, comment="0-1")
    conflict_level = Column(Float, comment="0-1")

    # Overall Strength
    relationship_strength = Column(Float, comment="-1 to 1, negative=hostile, positive=close")

    # Changes
    key_moments = Column(JSON, default=list, comment="""
        [
            {
                'chapter': 5,
                'event': 'Betrayal revealed',
                'impact': -0.8,
                'change': 'trust_level decreased from 0.9 to 0.1'
            }
        ]
    """)

    current_status = Column(Text, comment="Where the relationship stands now")
    trajectory = Column(String(50), comment="improving, declining, stable, volatile")

    # Context
    last_interaction_chapter = Column(Integer)
    last_interaction_type = Column(String(100), comment="conflict, collaboration, etc.")

    # Indexes for efficient queries
    __table_args__ = (
        # Composite index for querying relationship at specific chapter
        {'sqlite_autoincrement': True}
    )
