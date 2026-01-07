"""
Pydantic schemas for Planner API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== Book Arc Schemas =====

class BookArcCreate(BaseModel):
    """Create book arc"""
    project_id: int
    premise: str = Field(..., min_length=10, description="One-sentence story premise")
    theme: str = Field(..., min_length=5, description="Central thematic question")
    genre: Optional[str] = None

    # Act structure
    act1_end_chapter: Optional[int] = Field(None, ge=1)
    act2_end_chapter: Optional[int] = Field(None, ge=1)

    # Story beats
    inciting_incident: Optional[Dict[str, Any]] = None
    first_plot_point: Optional[Dict[str, Any]] = None
    midpoint: Optional[Dict[str, Any]] = None
    all_is_lost: Optional[Dict[str, Any]] = None
    climax: Optional[Dict[str, Any]] = None
    resolution: Optional[Dict[str, Any]] = None
    custom_beats: Optional[List[Dict[str, Any]]] = None

    # Tension curve
    tension_curve: Optional[List[Dict[str, Any]]] = None


class BookArcUpdate(BaseModel):
    """Update book arc"""
    premise: Optional[str] = Field(None, min_length=10)
    theme: Optional[str] = Field(None, min_length=5)
    genre: Optional[str] = None
    act1_end_chapter: Optional[int] = Field(None, ge=1)
    act2_end_chapter: Optional[int] = Field(None, ge=1)
    inciting_incident: Optional[Dict[str, Any]] = None
    first_plot_point: Optional[Dict[str, Any]] = None
    midpoint: Optional[Dict[str, Any]] = None
    all_is_lost: Optional[Dict[str, Any]] = None
    climax: Optional[Dict[str, Any]] = None
    resolution: Optional[Dict[str, Any]] = None
    custom_beats: Optional[List[Dict[str, Any]]] = None
    tension_curve: Optional[List[Dict[str, Any]]] = None


class BookArcResponse(BaseModel):
    """Book arc response"""
    id: int
    project_id: int
    premise: str
    theme: str
    genre: Optional[str]
    act1_end_chapter: Optional[int]
    act2_end_chapter: Optional[int]
    inciting_incident: Dict[str, Any]
    first_plot_point: Dict[str, Any]
    midpoint: Dict[str, Any]
    all_is_lost: Dict[str, Any]
    climax: Dict[str, Any]
    resolution: Dict[str, Any]
    custom_beats: List[Dict[str, Any]]
    tension_curve: List[Dict[str, Any]]
    validated: bool
    validation_notes: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Chapter Schemas =====

class ChapterCreate(BaseModel):
    """Create chapter"""
    project_id: int
    chapter_number: int = Field(..., ge=1)
    title: Optional[str] = None
    book_arc_id: Optional[int] = None

    # Purpose
    goal: str = Field(..., min_length=10, description="What this chapter must accomplish")
    stakes: Optional[str] = None
    conflict: Optional[str] = None

    # Emotional journey
    opening_emotion: Optional[str] = None
    closing_emotion: Optional[str] = None
    emotional_change: Optional[str] = None

    # Reveals
    reveals: Optional[List[str]] = None

    # Structure
    pov_character_id: Optional[int] = None
    primary_location_id: Optional[int] = None

    # Target
    target_word_count: int = Field(default=3000, ge=500, le=15000)
    target_tension: int = Field(default=50, ge=0, le=100)

    # Active elements
    active_threads: Optional[List[int]] = None
    active_promises: Optional[List[int]] = None


class ChapterUpdate(BaseModel):
    """Update chapter"""
    title: Optional[str] = None
    goal: Optional[str] = Field(None, min_length=10)
    stakes: Optional[str] = None
    conflict: Optional[str] = None
    opening_emotion: Optional[str] = None
    closing_emotion: Optional[str] = None
    emotional_change: Optional[str] = None
    reveals: Optional[List[str]] = None
    pov_character_id: Optional[int] = None
    primary_location_id: Optional[int] = None
    status: Optional[str] = None  # planned, drafted, revised, final
    target_word_count: Optional[int] = Field(None, ge=500, le=15000)
    target_tension: Optional[int] = Field(None, ge=0, le=100)
    tension_level: Optional[int] = Field(None, ge=0, le=100)
    active_threads: Optional[List[int]] = None
    active_promises: Optional[List[int]] = None
    content: Optional[str] = None  # Prose content


class ChapterResponse(BaseModel):
    """Chapter response"""
    id: int
    project_id: int
    book_arc_id: Optional[int]
    chapter_number: int
    title: Optional[str]
    goal: str
    stakes: Optional[str]
    conflict: Optional[str]
    opening_emotion: Optional[str]
    closing_emotion: Optional[str]
    emotional_change: Optional[str]
    reveals: List[str]
    pov_character_id: Optional[int]
    primary_location_id: Optional[int]
    status: str
    word_count: int
    target_word_count: int
    tension_level: int
    target_tension: int
    active_threads: List[int]
    active_promises: List[int]
    canon_version_id: Optional[int]
    prose_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Scene Schemas =====

class SceneCreate(BaseModel):
    """Create scene card"""
    chapter_id: int
    project_id: int
    scene_number: int = Field(..., ge=1)
    scene_type: Optional[str] = None  # action, dialogue, exposition, transition

    # Purpose
    goal: str = Field(..., min_length=5, description="What must happen in this scene")
    conflict: Optional[str] = None
    disaster: Optional[str] = None

    # Change
    entering_value: Optional[str] = None
    exiting_value: Optional[str] = None
    what_changes: str = Field(..., min_length=5, description="Concrete change that occurs")

    # Participants
    participants: List[int] = Field(default_factory=list, description="Character IDs")
    location_id: Optional[int] = None

    # Props
    required_items: Optional[List[int]] = None
    required_knowledge: Optional[List[str]] = None

    # Timing
    duration: Optional[str] = None
    time_of_day: Optional[str] = None

    # Generation hints
    tone: Optional[str] = None
    pacing: Optional[str] = None  # slow, medium, fast
    focus: Optional[str] = None  # action, dialogue, internal, description


class SceneUpdate(BaseModel):
    """Update scene card"""
    scene_type: Optional[str] = None
    goal: Optional[str] = Field(None, min_length=5)
    conflict: Optional[str] = None
    disaster: Optional[str] = None
    entering_value: Optional[str] = None
    exiting_value: Optional[str] = None
    what_changes: Optional[str] = Field(None, min_length=5)
    participants: Optional[List[int]] = None
    location_id: Optional[int] = None
    required_items: Optional[List[int]] = None
    required_knowledge: Optional[List[str]] = None
    duration: Optional[str] = None
    time_of_day: Optional[str] = None
    tone: Optional[str] = None
    pacing: Optional[str] = None
    focus: Optional[str] = None
    status: Optional[str] = None  # planned, drafted, revised, final
    content: Optional[str] = None  # Generated prose


class SceneResponse(BaseModel):
    """Scene response"""
    id: int
    chapter_id: int
    project_id: int
    scene_number: int
    scene_type: Optional[str]
    goal: str
    conflict: Optional[str]
    disaster: Optional[str]
    entering_value: Optional[str]
    exiting_value: Optional[str]
    what_changes: str
    participants: List[int]
    location_id: Optional[int]
    required_items: List[int]
    required_knowledge: List[str]
    duration: Optional[str]
    time_of_day: Optional[str]
    tone: Optional[str]
    pacing: Optional[str]
    focus: Optional[str]
    status: str
    word_count: int
    validated: bool
    validation_notes: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Validation Schemas =====

class ValidationResult(BaseModel):
    """Validation result"""
    valid: bool
    issues: List[str]


# ===== Project Structure Schema =====

class ProjectStructureResponse(BaseModel):
    """Complete project structure"""
    arc: Optional[BookArcResponse]
    chapters: List[ChapterResponse]
    total_chapters: int
    total_scenes: int
    total_words: int
    completion: Dict[str, Any]


# ===== Bulk Operations =====

class ReorderScenesRequest(BaseModel):
    """Request to reorder scenes"""
    scene_order: List[int] = Field(..., min_length=1, description="Scene IDs in desired order")
