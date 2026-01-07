"""
Pydantic schemas for permissions and collaborator management
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CollaboratorInvite(BaseModel):
    """Invite a user to collaborate"""
    email: EmailStr
    role: str  # "viewer", "writer", "editor"
    auto_accept: bool = False  # For testing, skip email confirmation


class CollaboratorUpdate(BaseModel):
    """Update collaborator role"""
    role: Optional[str] = None  # "viewer", "writer", "editor"


class CollaboratorResponse(BaseModel):
    """Collaborator information with user details"""
    id: int
    project_id: int
    user_id: int
    user_name: str
    user_email: str
    user_avatar: Optional[str]
    role: str
    invited_at: datetime
    accepted_at: Optional[datetime]
    is_pending: bool
    project_title: Optional[str] = None  # Only for invitations list

    class Config:
        from_attributes = True


class UserProjectRole(BaseModel):
    """User's role and permissions for a project"""
    project_id: int
    user_id: int
    role: str  # "owner", "editor", "writer", "viewer"
    can_view: bool
    can_edit: bool
    can_write: bool
    can_manage: bool  # Only owner can manage collaborators
