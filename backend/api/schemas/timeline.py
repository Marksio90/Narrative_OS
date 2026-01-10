"""
Timeline API Schemas

Request and response models for timeline endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== Timeline Events ====================

class CreateTimelineEventRequest(BaseModel):
    """Create custom timeline event"""
    chapter_number: int = Field(..., description="Chapter number")
    title: str = Field(..., min_length=1, max_length=500, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    layer: str = Field("plot", description="Timeline layer (plot, character, theme, technical, consequence)")
    magnitude: float = Field(0.5, ge=0.0, le=1.0, description="Event importance 0-1")
    scene_number: Optional[int] = Field(None, description="Scene within chapter")
    position_weight: float = Field(0.0, ge=0.0, le=1.0, description="Position within chapter")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color")
    icon: Optional[str] = Field(None, description="Icon name")
    tags: List[str] = Field(default_factory=list, description="User tags")
    related_characters: List[int] = Field(default_factory=list, description="Character IDs")
    related_locations: List[int] = Field(default_factory=list, description="Location IDs")
    is_major_beat: bool = Field(False, description="Is major story beat")


class UpdateTimelineEventRequest(BaseModel):
    """Update timeline event"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    chapter_number: Optional[int] = None
    scene_number: Optional[int] = None
    position_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    layer: Optional[str] = None
    magnitude: Optional[float] = Field(None, ge=0.0, le=1.0)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    tags: Optional[List[str]] = None
    related_characters: Optional[List[int]] = None
    related_locations: Optional[List[int]] = None
    is_major_beat: Optional[bool] = None
    is_visible: Optional[bool] = None
    is_locked: Optional[bool] = None


class MoveEventRequest(BaseModel):
    """Move event to different chapter"""
    new_chapter: int = Field(..., description="Target chapter number")
    new_position_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="New position weight")


class TimelineEventResponse(BaseModel):
    """Timeline event response"""
    id: int
    project_id: int
    event_type: str
    source_id: Optional[int]
    source_table: Optional[str]
    chapter_number: int
    scene_number: Optional[int]
    position_weight: float
    start_chapter: Optional[int]
    end_chapter: Optional[int]
    duration_chapters: Optional[int]
    title: str
    description: Optional[str]
    layer: str
    tags: List[str]
    color: Optional[str]
    icon: Optional[str]
    magnitude: float
    is_major_beat: bool
    related_characters: List[int]
    related_locations: List[int]
    related_events: List[int]
    metadata: Dict[str, Any]
    is_custom: bool
    is_visible: bool
    is_locked: bool
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimelineEventsListResponse(BaseModel):
    """List of timeline events with metadata"""
    events: List[TimelineEventResponse]
    total_count: int
    chapter_range: tuple[int, int]
    layers_present: List[str]


class SyncTimelineRequest(BaseModel):
    """Request to sync timeline from sources"""
    force_full_sync: bool = Field(False, description="Force complete re-sync")


class SyncTimelineResponse(BaseModel):
    """Sync results"""
    synced_counts: Dict[str, int]
    total_synced: int
    conflicts_detected: int
    duration_seconds: float


# ==================== Conflicts ====================

class ConflictResponse(BaseModel):
    """Timeline conflict response"""
    id: int
    project_id: int
    conflict_type: str
    severity: str
    chapter_start: Optional[int]
    chapter_end: Optional[int]
    event_ids: List[int]
    title: str
    description: str
    suggestions: List[Dict[str, Any]]
    status: str
    resolution_note: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by_user_id: Optional[int]
    detection_method: Optional[str]
    confidence: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResolveConflictRequest(BaseModel):
    """Resolve a conflict"""
    resolution_note: Optional[str] = Field(None, description="Resolution notes")


class ConflictsListResponse(BaseModel):
    """List of conflicts with counts"""
    conflicts: List[ConflictResponse]
    total_count: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]


class DetectConflictsResponse(BaseModel):
    """Conflict detection results"""
    conflicts_detected: Dict[str, int]
    total_conflicts: int
    critical_count: int
    error_count: int
    warning_count: int
    info_count: int


# ==================== Views ====================

class CreateViewRequest(BaseModel):
    """Create saved timeline view"""
    name: str = Field(..., min_length=1, max_length=255, description="View name")
    description: Optional[str] = Field(None, description="View description")
    config: Dict[str, Any] = Field(..., description="View configuration")
    is_default: bool = Field(False, description="Set as default view")
    is_shared: bool = Field(False, description="Share with team")


class UpdateViewRequest(BaseModel):
    """Update timeline view"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_shared: Optional[bool] = None


class TimelineViewResponse(BaseModel):
    """Timeline view response"""
    id: int
    project_id: int
    user_id: Optional[int]
    name: str
    description: Optional[str]
    config: Dict[str, Any]
    is_default: bool
    is_shared: bool
    last_used_at: Optional[datetime]
    use_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Bookmarks ====================

class CreateBookmarkRequest(BaseModel):
    """Create timeline bookmark"""
    chapter_number: int = Field(..., description="Chapter to bookmark")
    title: str = Field(..., min_length=1, max_length=255, description="Bookmark title")
    notes: Optional[str] = Field(None, description="Bookmark notes")
    color: str = Field("#FFD700", pattern="^#[0-9A-Fa-f]{6}$", description="Bookmark color")
    icon: str = Field("bookmark", description="Icon name")
    sort_order: int = Field(0, description="Custom sort order")


class UpdateBookmarkRequest(BaseModel):
    """Update bookmark"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    notes: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class TimelineBookmarkResponse(BaseModel):
    """Timeline bookmark response"""
    id: int
    project_id: int
    user_id: int
    chapter_number: int
    title: str
    notes: Optional[str]
    color: str
    icon: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Query Filters ====================

class TimelineQueryParams(BaseModel):
    """Query parameters for timeline events"""
    chapter_start: Optional[int] = Field(None, description="Filter: chapter range start")
    chapter_end: Optional[int] = Field(None, description="Filter: chapter range end")
    event_types: Optional[List[str]] = Field(None, description="Filter: event types")
    layers: Optional[List[str]] = Field(None, description="Filter: layers")
    tags: Optional[List[str]] = Field(None, description="Filter: tags")
    only_visible: bool = Field(True, description="Only visible events")
    only_major_beats: bool = Field(False, description="Only major story beats")


class ConflictQueryParams(BaseModel):
    """Query parameters for conflicts"""
    conflict_types: Optional[List[str]] = Field(None, description="Filter: conflict types")
    severities: Optional[List[str]] = Field(None, description="Filter: severities")
    status: Optional[str] = Field(None, description="Filter: status (open, resolved, ignored)")
    chapter_start: Optional[int] = Field(None, description="Chapter range start")
    chapter_end: Optional[int] = Field(None, description="Chapter range end")


# ==================== Statistics ====================

class TimelineStatisticsResponse(BaseModel):
    """Timeline statistics and insights"""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_layer: Dict[str, int]
    chapter_range: tuple[int, int]
    major_beats_count: int
    custom_events_count: int
    total_conflicts: int
    open_conflicts: int
    conflicts_by_severity: Dict[str, int]
    avg_events_per_chapter: float
    chapters_with_no_events: List[int]
    chapters_with_major_beats: List[int]
    most_active_characters: List[Dict[str, Any]]
    pacing_score: Optional[float] = Field(None, description="Overall pacing score 0-1")


class TimelineHealthResponse(BaseModel):
    """Timeline health check"""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall health 0-1")
    pacing_score: float = Field(..., ge=0.0, le=1.0)
    consistency_score: float = Field(..., ge=0.0, le=1.0)
    coverage_score: float = Field(..., ge=0.0, le=1.0, description="Story coverage")
    issues: List[str]
    recommendations: List[str]
    conflicts_summary: Dict[str, int]
