"""
Planner Models

Book structure: Arc → Chapters → Scenes
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class BookArc(Base, TimestampMixin):
    """
    Overall book structure and story beats
    """
    __tablename__ = "book_arcs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # Core theme & premise
    premise = Column(Text, comment="One-sentence story premise")
    theme = Column(Text, comment="Central thematic question/statement")
    genre = Column(String(100))

    # Three-Act Structure
    act1_end_chapter = Column(Integer, comment="Where Act 1 ends")
    act2_end_chapter = Column(Integer, comment="Where Act 2 ends")

    # Key Story Beats
    inciting_incident = Column(JSON, default=dict, comment="""
        {
            'chapter': int,
            'description': 'text',
            'changes': 'what shifts in protagonist\'s world'
        }
    """)

    first_plot_point = Column(JSON, default=dict, comment="End of Act 1 - no turning back")
    midpoint = Column(JSON, default=dict, comment="False victory or false defeat")
    all_is_lost = Column(JSON, default=dict, comment="Dark night of the soul")
    climax = Column(JSON, default=dict, comment="Final confrontation")
    resolution = Column(JSON, default=dict, comment="New normal")

    # Additional beats (flexible)
    custom_beats = Column(JSON, default=list, comment="Genre-specific or custom beats")

    # Tension Arc
    tension_curve = Column(JSON, default=list, comment="""
        [
            {'chapter': 1, 'target_tension': 30},
            {'chapter': 5, 'target_tension': 60},
            ...
        ]
    """)

    # Validation
    validated = Column(Boolean, default=False)
    validation_notes = Column(JSON, default=list)


class ChapterPlan(Base, TimestampMixin):
    """
    Individual chapter plan with goal, conflict, and change
    (Story planning model - separate from actual manuscript chapters)
    """
    __tablename__ = "planned_chapters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    book_arc_id = Column(Integer, ForeignKey("book_arcs.id"), nullable=True)

    # Position
    chapter_number = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=True)

    # Purpose
    goal = Column(Text, nullable=False, comment="What this chapter must accomplish")
    stakes = Column(Text, comment="What's at risk")
    conflict = Column(Text, comment="Primary conflict")

    # Emotional journey
    opening_emotion = Column(String(100), comment="Emotional state at start")
    closing_emotion = Column(String(100), comment="Emotional state at end")
    emotional_change = Column(Text, comment="How emotion shifts")

    # Revelation
    reveals = Column(JSON, default=list, comment="What information/secrets are revealed")

    # Structure
    pov_character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    primary_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    # Tracking
    status = Column(String(50), default="planned", index=True)  # planned, drafted, revised, final
    word_count = Column(Integer, default=0)
    target_word_count = Column(Integer, default=3000)

    # Active elements
    active_threads = Column(JSON, default=list, comment="Thread IDs active in this chapter")
    active_promises = Column(JSON, default=list, comment="Promise IDs active in this chapter")

    # Quality metrics
    tension_level = Column(Integer, default=50, comment="Actual tension 0-100")
    target_tension = Column(Integer, default=50, comment="Target tension from arc")

    # Prose
    content = Column(Text, nullable=True, comment="Actual prose (if drafted)")
    prose_version = Column(Integer, default=1)

    # Canon version
    canon_version_id = Column(Integer, ForeignKey("canon_versions.id"), nullable=True)


class Scene(Base, TimestampMixin):
    """
    Scene card - building block of chapter plans
    """
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("planned_chapters.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # Position
    scene_number = Column(Integer, nullable=False, comment="Position within chapter")
    scene_type = Column(String(50), comment="action, dialogue, exposition, transition, etc.")

    # Purpose
    goal = Column(Text, nullable=False, comment="What must happen in this scene")
    conflict = Column(Text, comment="What opposes the goal")
    disaster = Column(Text, comment="How it goes wrong (or unexpectedly right)")

    # Change
    entering_value = Column(String(100), comment="Value at start (e.g., 'hope', 'trust')")
    exiting_value = Column(String(100), comment="Value at end")
    what_changes = Column(Text, nullable=False, comment="Concrete change that occurs")

    # Participants
    participants = Column(JSON, default=list, comment="Character IDs present")
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    # Props & Requirements
    required_items = Column(JSON, default=list, comment="Item IDs needed")
    required_knowledge = Column(JSON, default=list, comment="What characters must know")

    # Timing
    duration = Column(String(100), comment="e.g., '10 minutes', '3 hours'")
    time_of_day = Column(String(100), comment="morning, noon, night, etc.")

    # Generation hints
    tone = Column(String(100))
    pacing = Column(String(50), comment="slow, medium, fast")
    focus = Column(String(100), comment="action, dialogue, internal, description")

    # Status
    status = Column(String(50), default="planned")  # planned, drafted, revised, final

    # Prose
    content = Column(Text, nullable=True, comment="Generated/written prose")
    word_count = Column(Integer, default=0)

    # Quality
    validated = Column(Boolean, default=False)
    validation_notes = Column(JSON, default=list)


class CanonContract(Base, TimestampMixin):
    """
    Hard rules that cannot be violated during generation
    """
    __tablename__ = "canon_contracts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # Contract identity
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Rule type
    rule_type = Column(String(100), comment="world, character, magic, plot, style")

    # The actual constraint
    constraint = Column(Text, nullable=False, comment="Natural language rule")

    # Affected entities
    applies_to = Column(JSON, default=dict, comment="""
        {
            'entity_type': 'character'|'location'|'magic'|...,
            'entity_ids': [...]  # null = applies to all
        }
    """)

    # Severity
    severity = Column(String(50), default="must", comment="must, should, prefer")

    # Validation
    validation_prompt = Column(Text, comment="Prompt for LLM to validate compliance")

    # Status
    active = Column(Boolean, default=True, index=True)

    # Violations
    violation_count = Column(Integer, default=0)

    # Examples
    examples = Column(JSON, default=list, comment="""
        [
            {'valid': 'text of valid behavior', 'invalid': 'text of invalid behavior'}
        ]
    """)
