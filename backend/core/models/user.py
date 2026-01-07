"""
Modern User Authentication Models (2026)
Using FastAPI-Users pattern with async SQLAlchemy 2.0
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
import enum

from core.database.base import Base


class SubscriptionTier(enum.Enum):
    """Subscription tiers for monetization"""
    FREE = "free"
    PRO = "pro"
    STUDIO = "studio"


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    Modern async user model with FastAPI-Users integration

    Features:
    - Email verification
    - OAuth support (Google, GitHub)
    - Subscription management
    - Audit trail
    """
    __tablename__ = "users"

    # Primary key (FastAPI-Users requires this pattern)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FastAPI-Users required fields (inherited from SQLAlchemyBaseUserTable)
    # - email: str (unique, indexed)
    # - hashed_password: str
    # - is_active: bool
    # - is_superuser: bool
    # - is_verified: bool

    # Custom fields
    name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Subscription
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(100))

    # Usage tracking
    llm_calls_this_month: Mapped[int] = mapped_column(Integer, default=0)
    storage_used_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Audit
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    collaborations: Mapped[list["ProjectCollaborator"]] = relationship(
        "ProjectCollaborator",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, tier={self.subscription_tier})>"


class CollaboratorRole(enum.Enum):
    """Roles for project collaboration with fine-grained permissions"""
    OWNER = "owner"        # Full control
    EDITOR = "editor"      # Can edit everything except settings
    WRITER = "writer"      # Can write prose, limited canon editing
    VIEWER = "viewer"      # Read-only access


class ProjectCollaborator(Base):
    """
    Many-to-many relationship between users and projects with roles
    """
    __tablename__ = "project_collaborators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    role: Mapped[CollaboratorRole] = mapped_column(
        SQLEnum(CollaboratorRole),
        nullable=False
    )
    invited_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    invited_by: Mapped[Optional[int]] = mapped_column(Integer)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="collaborations")

    def __repr__(self):
        return f"<ProjectCollaborator(project={self.project_id}, user={self.user_id}, role={self.role})>"


class OAuthAccount(Base):
    """
    OAuth provider accounts (Google, GitHub, etc.)
    FastAPI-Users OAuth integration
    """
    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    oauth_name: Mapped[str] = mapped_column(String(50), nullable=False)  # "google", "github"
    access_token: Mapped[str] = mapped_column(String(500), nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(500))
    expires_at: Mapped[Optional[int]] = mapped_column(Integer)
    account_id: Mapped[str] = mapped_column(String(320), nullable=False)  # OAuth provider user ID
    account_email: Mapped[str] = mapped_column(String(320), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<OAuthAccount(user={self.user_id}, provider={self.oauth_name})>"


# Update Project model to include owner_id (will be in separate migration)
"""
ALTER TABLE projects ADD COLUMN owner_id INTEGER REFERENCES users(id);
ALTER TABLE projects ADD COLUMN visibility VARCHAR(20) DEFAULT 'private';
CREATE INDEX idx_projects_owner ON projects(owner_id);
"""
