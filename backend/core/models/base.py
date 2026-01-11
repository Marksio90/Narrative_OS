"""
Base models and mixins for all Canon entities
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.base import Base


class TimestampMixin:
    """
    Mixin for created_at and updated_at timestamps
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CanonEntityMixin(TimestampMixin):
    """
    Base mixin for all Canon entities

    All entities have:
    - claims: established facts (JSON)
    - unknowns: deliberately undefined aspects (JSON)
    - version tracking
    """

    # Core identity
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Canon-specific: facts vs unknowns
    claims = Column(JSON, default=dict, nullable=False, comment="Established facts")
    unknowns = Column(JSON, default=list, nullable=False, comment="Deliberately undefined")

    # Versioning
    canon_version_id = Column(Integer, ForeignKey("canon_versions.id"), nullable=True, index=True)

    # Tags for organization
    tags = Column(JSON, default=list, nullable=False)

    @declared_attr
    def project_id(cls):
        return Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)


class Project(Base, TimestampMixin):
    """
    A book/novel project
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(100), index=True)  # fantasy, thriller, etc.
    target_word_count = Column(Integer, default=80000)

    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Status
    status = Column(String(50), default="draft")  # draft, in_progress, completed

    # Project metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    project_metadata = Column(JSON, default=dict)


class User(Base, TimestampMixin):
    """
    User/Author
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Subscription tier
    tier = Column(String(50), default="free")  # free, pro, studio

    # Settings
    settings = Column(JSON, default=dict)


class CanonVersion(Base, TimestampMixin):
    """
    Git-like versioning for Canon
    Each change to canon entities creates a new version
    """
    __tablename__ = "canon_versions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # Version info
    version_number = Column(Integer, nullable=False)
    commit_message = Column(Text)

    # Parent version (for rollback)
    parent_version_id = Column(Integer, ForeignKey("canon_versions.id"), nullable=True)

    # Author
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Snapshot of changes
    changes = Column(JSON, default=dict, comment="What changed in this version")
