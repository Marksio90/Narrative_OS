"""
Canon Database Models

All core narrative entities that form the "source of truth"
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
import enum
from .base import Base, CanonEntityMixin
from ..database.base import Base as SQLBase


class Character(Base, CanonEntityMixin):
    """
    Character entity with psychological depth and behavioral constraints
    """
    __tablename__ = "characters"

    # Psychological core
    goals = Column(JSON, default=list, comment="What they want")
    values = Column(JSON, default=list, comment="What they believe in")
    fears = Column(JSON, default=list, comment="What they fear")
    secrets = Column(JSON, default=list, comment="What they hide")

    # Behavioral constraints (for validation)
    behavioral_limits = Column(JSON, default=list, comment="What they would never do")
    behavioral_patterns = Column(JSON, default=list, comment="How they typically act")

    # Voice & Dialog
    voice_profile = Column(JSON, default=dict, comment="""
        {
            'sentence_length': 'short'|'medium'|'long',
            'formality': 0-100,
            'emotion_level': 0-100,
            'favorite_phrases': [],
            'forbidden_words': [],
            'dialect_markers': []
        }
    """)

    # Relationships (JSON for flexibility)
    relationships = Column(JSON, default=dict, comment="""
        {
            'character_id': {
                'type': 'friend'|'enemy'|'lover'|'family',
                'trust_level': 0-100,
                'history': 'text',
                'current_status': 'text'
            }
        }
    """)

    # Physical & Background
    appearance = Column(JSON, default=dict)
    background = Column(Text)

    # Arc tracking
    arc = Column(JSON, default=dict, comment="""
        {
            'starting_state': 'text',
            'lie_they_believe': 'text',
            'truth_they_need': 'text',
            'transformation_goal': 'text',
            'current_chapter': int
        }
    """)


class Location(Base, CanonEntityMixin):
    """
    Place/Location with rules and constraints
    """
    __tablename__ = "locations"

    # Geographic & Physical
    geography = Column(JSON, default=dict, comment="Terrain, climate, size")
    climate = Column(String(100))

    # Social rules
    social_rules = Column(JSON, default=list, comment="Cultural norms, laws, taboos")
    power_structure = Column(JSON, default=dict, comment="Who's in charge, factions present")

    # Restrictions (for validation)
    restrictions = Column(JSON, default=list, comment="What cannot happen here")
    access_control = Column(JSON, default=dict, comment="Who can enter, when, how")

    # Atmosphere
    atmosphere = Column(Text, comment="Mood, feeling, sensory details")

    # Connected locations
    connected_to = Column(JSON, default=list, comment="List of location IDs and travel info")


class Faction(Base, CanonEntityMixin):
    """
    Organization, group, or faction
    """
    __tablename__ = "factions"

    # Core identity
    interests = Column(JSON, default=list, comment="What they want")
    values = Column(JSON, default=list, comment="What they stand for")

    # Power & Resources
    resources = Column(JSON, default=dict, comment="Money, military, magic, influence")
    power_level = Column(Integer, default=50, comment="Overall power 0-100")

    # Relationships
    allies = Column(JSON, default=list, comment="Faction IDs")
    enemies = Column(JSON, default=list, comment="Faction IDs")
    neutral = Column(JSON, default=list, comment="Faction IDs")

    # Tactics & Methods
    tactics = Column(JSON, default=list, comment="How they operate")
    forbidden_actions = Column(JSON, default=list, comment="What they won't do")

    # Leadership
    leaders = Column(JSON, default=list, comment="Character IDs")
    hierarchy = Column(JSON, default=dict, comment="Organization structure")


class MagicRule(Base, CanonEntityMixin):
    """
    Magic system or world rule (HARD CONSTRAINTS)
    """
    __tablename__ = "magic_rules"

    # Rule type
    rule_type = Column(String(100), comment="magic, physics, divine, curse, etc.")

    # Laws (immutable)
    laws = Column(JSON, default=list, comment="Fundamental rules that ALWAYS apply")

    # Costs & Limitations
    costs = Column(JSON, default=list, comment="What using this requires/costs")
    limitations = Column(JSON, default=list, comment="What it cannot do")

    # Exceptions (rare, must be justified)
    exceptions = Column(JSON, default=list, comment="Rare cases where rules don't apply")

    # Prohibitions (for validation)
    prohibitions = Column(JSON, default=list, comment="What is strictly forbidden")

    # Mechanics
    mechanics = Column(Text, comment="How it works in practice")
    manifestation = Column(JSON, default=dict, comment="How it appears, feels, looks")


class Item(Base, CanonEntityMixin):
    """
    Artifact, item, or object of significance
    """
    __tablename__ = "items"

    # Properties
    properties = Column(JSON, default=dict, comment="Magical/special properties")
    limitations = Column(JSON, default=list, comment="What it can't do")

    # History & Lore
    history = Column(Text, comment="Origin story, past owners")
    significance = Column(Text, comment="Why it matters")

    # Access & Location
    current_owner = Column(Integer, ForeignKey("characters.id"), nullable=True)
    current_location = Column(Integer, ForeignKey("locations.id"), nullable=True)
    access_restrictions = Column(JSON, default=list, comment="Who can use it")

    # Physical
    appearance = Column(Text)
    condition = Column(String(100), comment="pristine, worn, damaged, etc.")


class Event(Base, CanonEntityMixin):
    """
    Significant event in timeline with causal relationships
    """
    __tablename__ = "events"

    # Timeline
    chapter_number = Column(Integer, nullable=True, index=True)
    scene_number = Column(Integer, nullable=True)
    relative_time = Column(String(255), comment="e.g., '3 days before Chapter 1'")

    # Causality
    causes = Column(JSON, default=list, comment="Event IDs that caused this")
    effects = Column(JSON, default=list, comment="Event IDs caused by this")

    # Consequences
    consequences = Column(JSON, default=list, comment="""
        [
            {
                'description': 'text',
                'affects': ['character_id', 'location_id', ...],
                'timeline': 'immediate'|'short_term'|'long_term',
                'resolved': bool
            }
        ]
    """)

    # Participants
    participants = Column(JSON, default=list, comment="Character IDs involved")
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    # Impact
    impact_level = Column(Integer, default=50, comment="How significant 0-100")


class Promise(Base, CanonEntityMixin):
    """
    Narrative promise (setup) that requires payoff
    """
    __tablename__ = "promises"

    # Setup
    setup_chapter = Column(Integer, nullable=False, index=True)
    setup_scene = Column(Integer, nullable=True)
    setup_description = Column(Text, nullable=False)

    # Required Payoff
    payoff_required = Column(Text, nullable=False, comment="What must happen to fulfill this")
    payoff_deadline = Column(Integer, nullable=True, comment="Chapter by which payoff must occur")

    # Status
    status = Column(String(50), default="open", index=True)  # open, fulfilled, abandoned

    # Actual Payoff
    payoff_chapter = Column(Integer, nullable=True)
    payoff_scene = Column(Integer, nullable=True)
    payoff_description = Column(Text, nullable=True)

    # Validation
    validated = Column(JSON, default=dict, comment="Validation result from QC")


class Thread(Base, CanonEntityMixin):
    """
    Narrative thread/subplot that spans multiple chapters
    """
    __tablename__ = "threads"

    # Thread type
    thread_type = Column(String(100), comment="plot, subplot, character_arc, mystery, romance")

    # Lifecycle
    start_chapter = Column(Integer, nullable=False, index=True)
    end_chapter = Column(Integer, nullable=True)
    status = Column(String(50), default="active", index=True)  # active, resolved, abandoned

    # Tracking
    current_chapter = Column(Integer, nullable=True)
    tension_level = Column(Integer, default=50, comment="Current tension 0-100")
    stakes = Column(Text, comment="What's at risk")

    # Deadline
    deadline = Column(Integer, nullable=True, comment="Chapter by which thread must resolve")

    # Milestones
    milestones = Column(JSON, default=list, comment="""
        [
            {
                'chapter': int,
                'description': 'text',
                'completed': bool
            }
        ]
    """)

    # Related entities
    related_characters = Column(JSON, default=list)
    related_promises = Column(JSON, default=list)


class StyleProfile(Base, CanonEntityMixin):
    """
    Prose style profile for consistent generation
    """
    __tablename__ = "style_profiles"

    # Scope: entire book or specific character/narrator
    scope = Column(String(50), default="book")  # book, character, narrator
    scope_id = Column(Integer, nullable=True, comment="Character ID if character scope")

    # Sentence Structure
    sentence_length = Column(String(50), default="medium")  # short, medium, long, varied
    sentence_complexity = Column(String(50), default="medium")  # simple, medium, complex

    # Vocabulary
    vocabulary_level = Column(String(50), default="medium")  # simple, medium, advanced, literary
    forbidden_words = Column(JSON, default=list)
    preferred_words = Column(JSON, default=list)

    # Tone & Atmosphere
    tone = Column(String(100))  # dark, humorous, epic, intimate, etc.
    formality = Column(Integer, default=50, comment="0=casual, 100=formal")
    emotion_intensity = Column(Integer, default=50, comment="0=understated, 100=intense")

    # Pacing
    default_tempo = Column(String(50), default="medium")  # slow, medium, fast
    scene_length_preference = Column(String(50), default="medium")

    # Literary Devices
    metaphor_frequency = Column(String(50), default="moderate")  # rare, moderate, frequent
    sensory_detail_level = Column(String(50), default="moderate")

    # Genre-Specific
    brutality_level = Column(Integer, default=50, comment="Violence/darkness 0-100")
    humor_level = Column(Integer, default=50, comment="0=serious, 100=comedic")

    # Narrator
    narrator_type = Column(String(50), default="third_limited")  # first, third_limited, third_omniscient
    narrator_distance = Column(String(50), default="close")  # close, moderate, distant

    # Examples (for few-shot learning)
    example_paragraphs = Column(JSON, default=list, comment="Sample prose in this style")
