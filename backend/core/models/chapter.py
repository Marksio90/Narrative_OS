"""
Chapter Database Model

Represents a chapter/scene in a project
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin


class Chapter(Base, TimestampMixin):
    """
    Chapter/Scene entity

    Stores manuscript content with versioning and metadata
    """
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # Ordering
    chapter_number = Column(Integer, nullable=False, index=True)
    scene_number = Column(Integer, nullable=True, comment="Scene number within chapter")

    # Content
    title = Column(String(255), nullable=False)
    content = Column(Text, comment="Chapter text content (Markdown or HTML)")
    summary = Column(Text, comment="Brief chapter summary")

    # POV & Perspective
    pov_character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    narrator_type = Column(String(50), default="third_limited", comment="first, third_limited, third_omniscient")

    # Word count tracking
    word_count = Column(Integer, default=0)
    target_word_count = Column(Integer, default=3000, comment="Target words for this chapter")

    # Status
    status = Column(String(50), default="draft", index=True, comment="draft, in_progress, complete, revision")
    is_published = Column(Boolean, default=False, comment="Whether chapter is published")

    # Metadata
    notes = Column(Text, comment="Writer's notes for this chapter")
    tags = Column(JSON, default=list, comment="Tags for organization")

    # Timestamps for writing sessions
    started_at = Column(DateTime, nullable=True, comment="When writing started")
    completed_at = Column(DateTime, nullable=True, comment="When chapter was completed")
    last_edited_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # AI assistance tracking
    ai_assisted = Column(Boolean, default=False, comment="Whether AI helped write this")
    ai_metadata = Column(JSON, default=dict, comment="AI generation metadata")

    # Version control
    version = Column(Integer, default=1, comment="Current version number")
    parent_version_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, comment="Previous version")

    # Metadata storage (renamed from 'metadata' to avoid SQLAlchemy conflict)
    chapter_metadata = Column(JSON, default=dict, comment="""
        {
            'location_ids': [int],
            'character_ids': [int],
            'event_ids': [int],
            'promise_ids': [int],
            'timeline_position': 'string',
            'tension_level': 0-100,
            'pacing': 'slow'|'medium'|'fast'
        }
    """)


class ChapterVersion(Base, TimestampMixin):
    """
    Chapter version history for rollback functionality

    Stores snapshots of chapter content
    """
    __tablename__ = "chapter_versions"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)

    # Version info
    version_number = Column(Integer, nullable=False)
    commit_message = Column(String(500), comment="What changed in this version")

    # Snapshot
    content_snapshot = Column(Text, nullable=False, comment="Full chapter content at this version")
    word_count_snapshot = Column(Integer, default=0)
    metadata_snapshot = Column(JSON, default=dict)

    # Author
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Auto-save vs manual save
    is_autosave = Column(Boolean, default=False)


class WritingSession(Base, TimestampMixin):
    """
    Track writing sessions for analytics

    Records when user writes and how much
    """
    __tablename__ = "writing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)

    # Session metrics
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0, comment="Total active writing time")

    # Writing metrics
    words_added = Column(Integer, default=0)
    words_deleted = Column(Integer, default=0)
    net_words = Column(Integer, default=0, comment="Added - Deleted")

    # Activity
    keystrokes = Column(Integer, default=0, comment="Total keystrokes")
    ai_generations = Column(Integer, default=0, comment="Number of AI assists used")

    # Environment (renamed from 'metadata' to avoid SQLAlchemy conflict)
    session_metadata = Column(JSON, default=dict, comment="""
        {
            'device': 'string',
            'session_notes': 'string',
            'mood': 'string',
            'goals_met': bool
        }
    """)
