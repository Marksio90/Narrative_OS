"""
Chapter Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChapterBase(BaseModel):
    """Base chapter fields"""
    title: str = Field(..., min_length=1, max_length=255)
    chapter_number: int = Field(..., ge=1)
    scene_number: Optional[int] = Field(None, ge=1)
    content: str = Field(default="", description="Chapter text content")
    summary: Optional[str] = None
    pov_character_id: Optional[int] = None
    narrator_type: str = Field(default="third_limited")
    target_word_count: int = Field(default=3000, ge=0)
    status: str = Field(default="draft", pattern="^(draft|in_progress|complete|revision)$")
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChapterCreate(ChapterBase):
    """Create new chapter"""
    pass


class ChapterUpdate(BaseModel):
    """Update chapter (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    chapter_number: Optional[int] = Field(None, ge=1)
    scene_number: Optional[int] = Field(None, ge=1)
    content: Optional[str] = None
    summary: Optional[str] = None
    pov_character_id: Optional[int] = None
    narrator_type: Optional[str] = None
    target_word_count: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(draft|in_progress|complete|revision)$")
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChapterResponse(ChapterBase):
    """Full chapter response"""
    id: int
    project_id: int
    word_count: int
    is_published: bool
    ai_assisted: bool
    version: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_edited_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterListItem(BaseModel):
    """Lightweight chapter list item"""
    id: int
    project_id: int
    chapter_number: int
    scene_number: Optional[int]
    title: str
    word_count: int
    status: str
    last_edited_at: datetime

    class Config:
        from_attributes = True


class ChapterListResponse(BaseModel):
    """List of chapters"""
    chapters: List[ChapterListItem]
    total: int


class ChapterVersionResponse(BaseModel):
    """Chapter version history item"""
    id: int
    chapter_id: int
    version_number: int
    commit_message: Optional[str]
    word_count_snapshot: int
    is_autosave: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WritingSessionCreate(BaseModel):
    """Start a writing session"""
    chapter_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WritingSessionUpdate(BaseModel):
    """Update writing session"""
    words_added: Optional[int] = None
    words_deleted: Optional[int] = None
    keystrokes: Optional[int] = None
    ai_generations: Optional[int] = None


class WritingSessionEnd(BaseModel):
    """End a writing session"""
    words_added: int = 0
    words_deleted: int = 0
    keystrokes: int = 0
    ai_generations: int = 0
    session_notes: Optional[str] = None


class WritingSessionResponse(BaseModel):
    """Writing session response"""
    id: int
    user_id: int
    project_id: int
    chapter_id: Optional[int]
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: int
    words_added: int
    words_deleted: int
    net_words: int
    keystrokes: int
    ai_generations: int
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class ChapterAutoSaveRequest(BaseModel):
    """Auto-save chapter content"""
    content: str
    word_count: int
    cursor_position: Optional[int] = None


class ChapterReorderRequest(BaseModel):
    """Reorder chapters"""
    chapter_orders: List[Dict[str, int]] = Field(
        ...,
        description="List of {chapter_id: int, new_number: int}"
    )
