"""
Timeline Visualizer Models

Unified timeline view across all project elements
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Float, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import Base, TimestampMixin


class TimelineEventType(enum.Enum):
    """Types of events on the timeline"""
    CHAPTER = "chapter"
    STORY_EVENT = "story_event"
    MILESTONE = "milestone"
    BEAT = "beat"
    CONSEQUENCE = "consequence"
    CUSTOM = "custom"


class TimelineLayer(enum.Enum):
    """Visual layers for timeline organization"""
    PLOT = "plot"  # Main plot events
    CHARACTER = "character"  # Character arc milestones
    THEME = "theme"  # Thematic beats
    TECHNICAL = "technical"  # Chapters, structure
    CONSEQUENCE = "consequence"  # Consequences and ripples


class ConflictType(enum.Enum):
    """Types of timeline conflicts"""
    OVERLAP = "overlap"  # Events at same position
    INCONSISTENCY = "inconsistency"  # Logic conflicts
    PACING_ISSUE = "pacing_issue"  # Too fast/slow
    CHARACTER_CONFLICT = "character_conflict"  # Character in two places
    CONTINUITY_ERROR = "continuity_error"  # Timeline doesn't make sense


class ConflictSeverity(enum.Enum):
    """How severe is the conflict"""
    INFO = "info"  # FYI, not necessarily a problem
    WARNING = "warning"  # Should review
    ERROR = "error"  # Needs fixing
    CRITICAL = "critical"  # Breaks story logic


class TimelineEvent(Base, TimestampMixin):
    """
    Unified timeline event

    Aggregates all timeline-relevant data from various sources
    into a single, queryable view for visualization.
    """
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Event type and source
    event_type = Column(Enum(TimelineEventType), nullable=False, index=True)
    source_id = Column(Integer, nullable=True, comment="ID in source table (chapter_id, event_id, etc.)")
    source_table = Column(String(50), nullable=True, comment="Source table name")

    # Timeline position
    chapter_number = Column(Integer, nullable=False, index=True, comment="Primary timeline position")
    scene_number = Column(Integer, nullable=True, comment="Sub-position within chapter")

    # For relative positioning within same chapter/scene
    position_weight = Column(Float, default=0.0, comment="0-1 value for ordering events in same chapter")

    # Temporal range (for multi-chapter events like arcs)
    start_chapter = Column(Integer, nullable=True)
    end_chapter = Column(Integer, nullable=True)
    duration_chapters = Column(Integer, nullable=True, comment="Calculated duration")

    # Event details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Categorization
    layer = Column(Enum(TimelineLayer), nullable=False, default=TimelineLayer.PLOT, index=True)
    tags = Column(JSON, default=list, comment="User-defined tags for filtering")

    # Visual properties
    color = Column(String(7), nullable=True, comment="Hex color for visualization")
    icon = Column(String(50), nullable=True, comment="Icon name for display")

    # Importance
    magnitude = Column(Float, default=0.5, comment="Event importance 0-1")
    is_major_beat = Column(Boolean, default=False, comment="Is this a major story beat?")

    # Relationships (stored as JSON arrays of IDs)
    related_characters = Column(JSON, default=list, comment="Character IDs involved")
    related_locations = Column(JSON, default=list, comment="Location IDs")
    related_events = Column(JSON, default=list, comment="Other timeline event IDs")

    # Source-specific metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    event_metadata = Column(JSON, default=dict, comment="""
        Flexible storage for source-specific data:
        {
            'chapter': {
                'word_count': int,
                'status': str,
                'pov_character_id': int
            },
            'story_event': {
                'event_type': str,
                'emotional_impact': float
            },
            'milestone': {
                'arc_id': int,
                'milestone_type': str,
                'significance': int
            },
            'beat': {
                'beat_type': str,
                'act': int
            },
            'consequence': {
                'timeframe': str,
                'status': str,
                'probability': float
            }
        }
    """)

    # User customization
    is_custom = Column(Boolean, default=False, comment="User-created vs auto-generated")
    is_visible = Column(Boolean, default=True, comment="Shown in timeline")
    is_locked = Column(Boolean, default=False, comment="Prevent auto-updates")

    # Sync tracking
    last_synced_at = Column(DateTime, nullable=True, comment="When last synced from source")
    sync_hash = Column(String(64), nullable=True, comment="Hash of source data for change detection")


class TimelineConflict(Base, TimestampMixin):
    """
    Detected conflicts or issues in the timeline

    Automatically identifies problems like:
    - Characters in two places at once
    - Events that don't make logical sense
    - Pacing issues
    """
    __tablename__ = "timeline_conflicts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Conflict details
    conflict_type = Column(Enum(ConflictType), nullable=False, index=True)
    severity = Column(Enum(ConflictSeverity), nullable=False, default=ConflictSeverity.WARNING, index=True)

    # Location in timeline
    chapter_start = Column(Integer, nullable=True)
    chapter_end = Column(Integer, nullable=True)

    # Involved events
    event_ids = Column(JSON, nullable=False, default=list, comment="Timeline event IDs involved")

    # Description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, comment="What's the conflict?")

    # AI-generated suggestions
    suggestions = Column(JSON, default=list, comment="""
        [
            {
                'action': 'move_event' | 'remove_event' | 'edit_event',
                'event_id': int,
                'details': str
            }
        ]
    """)

    # Resolution
    status = Column(String(20), default="open", comment="open, acknowledged, resolved, ignored")
    resolution_note = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Auto-detection metadata
    detection_method = Column(String(50), nullable=True, comment="Which algorithm detected this")
    confidence = Column(Float, nullable=True, comment="0-1 confidence in detection")


class TimelineView(Base, TimestampMixin):
    """
    Saved timeline views/configurations

    Allows users to save and restore specific timeline states,
    filters, and zoom levels.
    """
    __tablename__ = "timeline_views"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # View details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Visual configuration
    config = Column(JSON, nullable=False, default=dict, comment="""
        {
            'zoom_level': float,
            'center_chapter': int,
            'enabled_layers': [str],
            'filters': {
                'event_types': [str],
                'tags': [str],
                'characters': [int],
                'magnitude_min': float
            },
            'layout': 'horizontal' | 'vertical',
            'grouping': 'chapter' | 'layer' | 'character',
            'show_conflicts': bool,
            'show_connections': bool
        }
    """)

    # Sharing
    is_default = Column(Boolean, default=False, comment="Default view for this user")
    is_shared = Column(Boolean, default=False, comment="Shared with team")

    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0)


class TimelineBookmark(Base, TimestampMixin):
    """
    User bookmarks on the timeline

    Quick navigation to important moments
    """
    __tablename__ = "timeline_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Bookmark position
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)

    # Visual
    color = Column(String(7), default="#FFD700", comment="Bookmark color")
    icon = Column(String(50), default="bookmark", comment="Icon name")

    # Order
    sort_order = Column(Integer, default=0, comment="User-defined ordering")
