"""
Project Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project fields"""
    title: str = Field(..., min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    target_word_count: int = Field(default=80000, ge=0)
    status: str = Field(default="draft", pattern="^(draft|in_progress|completed|archived)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    """Create new project"""
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Update project (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    target_word_count: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(draft|in_progress|completed|archived)$")
    metadata: Optional[Dict[str, Any]] = None


class ProjectStats(BaseModel):
    """Project statistics"""
    current_word_count: int = 0
    chapters_count: int = 0
    characters_count: int = 0
    locations_count: int = 0
    threads_count: int = 0
    promises_count: int = 0
    last_edited: Optional[datetime] = None
    completion_percent: float = 0.0


class ProjectResponse(ProjectBase):
    """Full project response"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    stats: Optional[ProjectStats] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """List of projects with stats"""
    projects: list[ProjectResponse]
    total: int


class ProjectDuplicateRequest(BaseModel):
    """Duplicate project request"""
    new_title: str = Field(..., min_length=1)
    include_canon: bool = Field(default=True, description="Copy all canon entities")
    include_chapters: bool = Field(default=False, description="Copy chapter structure (not content)")
    include_settings: bool = Field(default=True, description="Copy project settings")


class ProjectArchiveRequest(BaseModel):
    """Archive/unarchive project"""
    archive: bool = Field(..., description="True to archive, False to unarchive")


class ProjectTransferRequest(BaseModel):
    """Transfer project ownership"""
    new_owner_id: int = Field(..., gt=0)
