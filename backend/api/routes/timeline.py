"""
Timeline Visualizer API Routes

RESTful endpoints for timeline management and visualization
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from core.database.base import get_db
from core.models.timeline import (
    TimelineEventType,
    TimelineLayer,
    ConflictType,
    ConflictSeverity,
)
from services.timeline_service import TimelineService
from api.schemas.timeline import (
    # Events
    CreateTimelineEventRequest,
    UpdateTimelineEventRequest,
    MoveEventRequest,
    TimelineEventResponse,
    TimelineEventsListResponse,
    SyncTimelineRequest,
    SyncTimelineResponse,
    # Conflicts
    ConflictResponse,
    ResolveConflictRequest,
    ConflictsListResponse,
    DetectConflictsResponse,
    # Views
    CreateViewRequest,
    UpdateViewRequest,
    TimelineViewResponse,
    # Bookmarks
    CreateBookmarkRequest,
    UpdateBookmarkRequest,
    TimelineBookmarkResponse,
    # Query params
    TimelineQueryParams,
    ConflictQueryParams,
    # Statistics
    TimelineStatisticsResponse,
    TimelineHealthResponse,
)

router = APIRouter()


def get_timeline_service(db: Session = Depends(get_db)) -> TimelineService:
    """Dependency to get timeline service"""
    return TimelineService(db=db)


# ==================== Timeline Events ====================

@router.post("/projects/{project_id}/timeline/sync", response_model=SyncTimelineResponse)
async def sync_project_timeline(
    project_id: int,
    request: SyncTimelineRequest,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Sync timeline from all data sources

    Aggregates events from:
    - Chapters
    - Story events
    - Character arc milestones
    - Book structure beats
    - Consequences
    """
    start_time = time.time()

    try:
        synced_counts = service.sync_project_timeline(project_id)
        total_synced = sum(synced_counts.values())

        # Get conflicts after sync
        conflicts = service.get_conflicts(project_id, status="open")

        duration = time.time() - start_time

        return SyncTimelineResponse(
            synced_counts=synced_counts,
            total_synced=total_synced,
            conflicts_detected=len(conflicts),
            duration_seconds=round(duration, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync timeline: {str(e)}"
        )


@router.get("/projects/{project_id}/timeline/events", response_model=TimelineEventsListResponse)
async def get_timeline_events(
    project_id: int,
    chapter_start: Optional[int] = Query(None, description="Filter by chapter range start"),
    chapter_end: Optional[int] = Query(None, description="Filter by chapter range end"),
    event_types: Optional[str] = Query(None, description="Comma-separated event types"),
    layers: Optional[str] = Query(None, description="Comma-separated layers"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    only_visible: bool = Query(True, description="Only visible events"),
    only_major_beats: bool = Query(False, description="Only major story beats"),
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Get timeline events with filtering

    Returns all events in the timeline with optional filters
    for chapter range, type, layer, tags, etc.
    """
    # Parse comma-separated strings
    event_types_list = [TimelineEventType[t.strip()] for t in event_types.split(",")] if event_types else None
    layers_list = [TimelineLayer[l.strip()] for l in layers.split(",")] if layers else None
    tags_list = [t.strip() for t in tags.split(",")] if tags else None

    events = service.get_timeline_events(
        project_id=project_id,
        chapter_start=chapter_start,
        chapter_end=chapter_end,
        event_types=event_types_list,
        layers=layers_list,
        tags=tags_list,
        only_visible=only_visible,
        only_major_beats=only_major_beats
    )

    if not events:
        return TimelineEventsListResponse(
            events=[],
            total_count=0,
            chapter_range=(0, 0),
            layers_present=[]
        )

    # Calculate metadata
    chapters = [e.chapter_number for e in events]
    chapter_range = (min(chapters), max(chapters))
    layers_present = list(set(e.layer.value for e in events))

    return TimelineEventsListResponse(
        events=[TimelineEventResponse.model_validate(e) for e in events],
        total_count=len(events),
        chapter_range=chapter_range,
        layers_present=layers_present
    )


@router.post("/projects/{project_id}/timeline/events", response_model=TimelineEventResponse, status_code=201)
async def create_custom_event(
    project_id: int,
    request: CreateTimelineEventRequest,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Create custom timeline event

    Allows users to add custom events to the timeline
    that aren't synced from other data sources.
    """
    try:
        layer_enum = TimelineLayer[request.layer]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid layer: {request.layer}"
        )

    event = service.create_custom_event(
        project_id=project_id,
        chapter_number=request.chapter_number,
        title=request.title,
        description=request.description,
        layer=layer_enum,
        magnitude=request.magnitude,
        scene_number=request.scene_number,
        position_weight=request.position_weight,
        color=request.color,
        icon=request.icon,
        tags=request.tags,
        related_characters=request.related_characters,
        related_locations=request.related_locations,
        is_major_beat=request.is_major_beat
    )

    return TimelineEventResponse.model_validate(event)


@router.get("/projects/{project_id}/timeline/events/{event_id}", response_model=TimelineEventResponse)
async def get_timeline_event(
    project_id: int,
    event_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """Get single timeline event by ID"""
    from core.models.timeline import TimelineEvent

    event = service.db.query(TimelineEvent).filter(
        TimelineEvent.id == event_id,
        TimelineEvent.project_id == project_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )

    return TimelineEventResponse.model_validate(event)


@router.put("/projects/{project_id}/timeline/events/{event_id}", response_model=TimelineEventResponse)
async def update_timeline_event(
    project_id: int,
    event_id: int,
    request: UpdateTimelineEventRequest,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Update timeline event

    Can update custom events or unlocked synced events.
    Locked events cannot be modified.
    """
    # Build updates dict
    updates = {}
    for field, value in request.model_dump(exclude_unset=True).items():
        if value is not None:
            updates[field] = value

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )

    event = service.update_event(event_id, **updates)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found or is locked"
        )

    return TimelineEventResponse.model_validate(event)


@router.delete("/projects/{project_id}/timeline/events/{event_id}", status_code=204)
async def delete_timeline_event(
    project_id: int,
    event_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Delete timeline event

    Only custom events can be deleted.
    Synced events are hidden by setting is_visible=false.
    """
    success = service.delete_event(event_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found or cannot be deleted (not custom)"
        )

    return None


@router.post("/projects/{project_id}/timeline/events/{event_id}/move", response_model=TimelineEventResponse)
async def move_timeline_event(
    project_id: int,
    event_id: int,
    request: MoveEventRequest,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Move event to different chapter/position

    Useful for drag-and-drop functionality.
    Cannot move locked events.
    """
    event = service.move_event(
        event_id=event_id,
        new_chapter=request.new_chapter,
        new_position_weight=request.new_position_weight
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found or is locked"
        )

    return TimelineEventResponse.model_validate(event)


# ==================== Conflicts ====================

@router.post("/projects/{project_id}/timeline/conflicts/detect", response_model=DetectConflictsResponse)
async def detect_timeline_conflicts(
    project_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Run conflict detection

    Analyzes timeline for:
    - Event overlaps
    - Character conflicts
    - Pacing issues
    - Continuity errors
    """
    try:
        conflicts_detected = service.detect_all_conflicts(project_id)
        total = sum(conflicts_detected.values())

        # Get severity counts
        conflicts = service.get_conflicts(project_id, status="open")
        severity_counts = {
            "critical": len([c for c in conflicts if c.severity == ConflictSeverity.CRITICAL]),
            "error": len([c for c in conflicts if c.severity == ConflictSeverity.ERROR]),
            "warning": len([c for c in conflicts if c.severity == ConflictSeverity.WARNING]),
            "info": len([c for c in conflicts if c.severity == ConflictSeverity.INFO]),
        }

        return DetectConflictsResponse(
            conflicts_detected=conflicts_detected,
            total_conflicts=total,
            critical_count=severity_counts["critical"],
            error_count=severity_counts["error"],
            warning_count=severity_counts["warning"],
            info_count=severity_counts["info"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect conflicts: {str(e)}"
        )


@router.get("/projects/{project_id}/timeline/conflicts", response_model=ConflictsListResponse)
async def get_timeline_conflicts(
    project_id: int,
    conflict_types: Optional[str] = Query(None, description="Comma-separated conflict types"),
    severities: Optional[str] = Query(None, description="Comma-separated severities"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter"),
    chapter_start: Optional[int] = Query(None, description="Chapter range start"),
    chapter_end: Optional[int] = Query(None, description="Chapter range end"),
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Get timeline conflicts with filtering

    Returns all detected conflicts with optional filters.
    """
    # Parse filters
    conflict_types_list = None
    if conflict_types:
        try:
            conflict_types_list = [ConflictType[t.strip()] for t in conflict_types.split(",")]
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid conflict type: {str(e)}"
            )

    severities_list = None
    if severities:
        try:
            severities_list = [ConflictSeverity[s.strip()] for s in severities.split(",")]
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity: {str(e)}"
            )

    chapter_range = None
    if chapter_start is not None and chapter_end is not None:
        chapter_range = (chapter_start, chapter_end)

    conflicts = service.get_conflicts(
        project_id=project_id,
        conflict_types=conflict_types_list,
        severities=severities_list,
        status=status_filter,
        chapter_range=chapter_range
    )

    # Calculate counts
    by_severity = {}
    for severity in ConflictSeverity:
        by_severity[severity.value] = len([c for c in conflicts if c.severity == severity])

    by_type = {}
    for conflict_type in ConflictType:
        by_type[conflict_type.value] = len([c for c in conflicts if c.conflict_type == conflict_type])

    return ConflictsListResponse(
        conflicts=[ConflictResponse.model_validate(c) for c in conflicts],
        total_count=len(conflicts),
        by_severity=by_severity,
        by_type=by_type
    )


@router.get("/projects/{project_id}/timeline/conflicts/{conflict_id}", response_model=ConflictResponse)
async def get_timeline_conflict(
    project_id: int,
    conflict_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """Get single conflict by ID"""
    from core.models.timeline import TimelineConflict

    conflict = service.db.query(TimelineConflict).filter(
        TimelineConflict.id == conflict_id,
        TimelineConflict.project_id == project_id
    ).first()

    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conflict {conflict_id} not found"
        )

    return ConflictResponse.model_validate(conflict)


@router.post("/projects/{project_id}/timeline/conflicts/{conflict_id}/resolve", response_model=ConflictResponse)
async def resolve_timeline_conflict(
    project_id: int,
    conflict_id: int,
    request: ResolveConflictRequest,
    user_id: Optional[int] = Query(None, description="User ID resolving conflict"),
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Mark conflict as resolved

    Records resolution note and timestamp.
    """
    conflict = service.resolve_conflict(
        conflict_id=conflict_id,
        resolution_note=request.resolution_note,
        user_id=user_id
    )

    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conflict {conflict_id} not found"
        )

    return ConflictResponse.model_validate(conflict)


@router.post("/projects/{project_id}/timeline/conflicts/{conflict_id}/ignore", response_model=ConflictResponse)
async def ignore_timeline_conflict(
    project_id: int,
    conflict_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Mark conflict as ignored

    User acknowledges but chooses not to fix.
    """
    conflict = service.ignore_conflict(conflict_id=conflict_id)

    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conflict {conflict_id} not found"
        )

    return ConflictResponse.model_validate(conflict)


# ==================== Views ====================

@router.post("/projects/{project_id}/timeline/views", response_model=TimelineViewResponse, status_code=201)
async def create_timeline_view(
    project_id: int,
    request: CreateViewRequest,
    user_id: Optional[int] = Query(None, description="User ID"),
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Save timeline view configuration

    Allows users to save their preferred timeline settings,
    filters, zoom levels, etc.
    """
    view = service.save_view(
        project_id=project_id,
        name=request.name,
        config=request.config,
        user_id=user_id,
        description=request.description,
        is_default=request.is_default
    )

    return TimelineViewResponse.model_validate(view)


@router.get("/projects/{project_id}/timeline/views", response_model=List[TimelineViewResponse])
async def get_timeline_views(
    project_id: int,
    user_id: Optional[int] = Query(None, description="User ID"),
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Get saved timeline views

    Returns user's views and shared views.
    """
    views = service.get_views(project_id=project_id, user_id=user_id)
    return [TimelineViewResponse.model_validate(v) for v in views]


@router.get("/projects/{project_id}/timeline/views/{view_id}", response_model=TimelineViewResponse)
async def get_timeline_view(
    project_id: int,
    view_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """Get single view by ID"""
    from core.models.timeline import TimelineView

    view = service.db.query(TimelineView).filter(
        TimelineView.id == view_id,
        TimelineView.project_id == project_id
    ).first()

    if not view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"View {view_id} not found"
        )

    return TimelineViewResponse.model_validate(view)


@router.put("/projects/{project_id}/timeline/views/{view_id}", response_model=TimelineViewResponse)
async def update_timeline_view(
    project_id: int,
    view_id: int,
    request: UpdateViewRequest,
    service: TimelineService = Depends(get_timeline_service)
):
    """Update timeline view"""
    from core.models.timeline import TimelineView

    view = service.db.query(TimelineView).filter(
        TimelineView.id == view_id,
        TimelineView.project_id == project_id
    ).first()

    if not view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"View {view_id} not found"
        )

    # Update fields
    for field, value in request.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(view, field, value)

    service.db.commit()
    service.db.refresh(view)

    return TimelineViewResponse.model_validate(view)


@router.delete("/projects/{project_id}/timeline/views/{view_id}", status_code=204)
async def delete_timeline_view(
    project_id: int,
    view_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """Delete timeline view"""
    from core.models.timeline import TimelineView

    view = service.db.query(TimelineView).filter(
        TimelineView.id == view_id,
        TimelineView.project_id == project_id
    ).first()

    if not view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"View {view_id} not found"
        )

    service.db.delete(view)
    service.db.commit()

    return None


# ==================== Bookmarks ====================

@router.post("/projects/{project_id}/timeline/bookmarks", response_model=TimelineBookmarkResponse, status_code=201)
async def create_timeline_bookmark(
    project_id: int,
    request: CreateBookmarkRequest,
    user_id: int = Query(..., description="User ID"),
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Create timeline bookmark

    Quick navigation markers for important chapters.
    """
    bookmark = service.create_bookmark(
        project_id=project_id,
        user_id=user_id,
        chapter_number=request.chapter_number,
        title=request.title,
        notes=request.notes,
        color=request.color
    )

    return TimelineBookmarkResponse.model_validate(bookmark)


@router.get("/projects/{project_id}/timeline/bookmarks", response_model=List[TimelineBookmarkResponse])
async def get_timeline_bookmarks(
    project_id: int,
    user_id: int = Query(..., description="User ID"),
    service: TimelineService = Depends(get_timeline_service)
):
    """Get user's bookmarks for project"""
    bookmarks = service.get_bookmarks(project_id=project_id, user_id=user_id)
    return [TimelineBookmarkResponse.model_validate(b) for b in bookmarks]


@router.put("/projects/{project_id}/timeline/bookmarks/{bookmark_id}", response_model=TimelineBookmarkResponse)
async def update_timeline_bookmark(
    project_id: int,
    bookmark_id: int,
    request: UpdateBookmarkRequest,
    service: TimelineService = Depends(get_timeline_service)
):
    """Update bookmark"""
    from core.models.timeline import TimelineBookmark

    bookmark = service.db.query(TimelineBookmark).filter(
        TimelineBookmark.id == bookmark_id,
        TimelineBookmark.project_id == project_id
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark {bookmark_id} not found"
        )

    # Update fields
    for field, value in request.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(bookmark, field, value)

    service.db.commit()
    service.db.refresh(bookmark)

    return TimelineBookmarkResponse.model_validate(bookmark)


@router.delete("/projects/{project_id}/timeline/bookmarks/{bookmark_id}", status_code=204)
async def delete_timeline_bookmark(
    project_id: int,
    bookmark_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """Delete bookmark"""
    from core.models.timeline import TimelineBookmark

    bookmark = service.db.query(TimelineBookmark).filter(
        TimelineBookmark.id == bookmark_id,
        TimelineBookmark.project_id == project_id
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark {bookmark_id} not found"
        )

    service.db.delete(bookmark)
    service.db.commit()

    return None


# ==================== Statistics ====================

@router.get("/projects/{project_id}/timeline/statistics", response_model=TimelineStatisticsResponse)
async def get_timeline_statistics(
    project_id: int,
    service: TimelineService = Depends(get_timeline_service)
):
    """
    Get timeline statistics and insights

    Provides overview of timeline health, event distribution,
    and character involvement.
    """
    events = service.get_timeline_events(project_id=project_id, only_visible=True)

    if not events:
        return TimelineStatisticsResponse(
            total_events=0,
            events_by_type={},
            events_by_layer={},
            chapter_range=(0, 0),
            major_beats_count=0,
            custom_events_count=0,
            total_conflicts=0,
            open_conflicts=0,
            conflicts_by_severity={},
            avg_events_per_chapter=0.0,
            chapters_with_no_events=[],
            chapters_with_major_beats=[],
            most_active_characters=[],
            pacing_score=None
        )

    # Calculate statistics
    chapters = [e.chapter_number for e in events]
    chapter_range = (min(chapters), max(chapters))
    chapter_span = chapter_range[1] - chapter_range[0] + 1

    events_by_type = {}
    for event_type in TimelineEventType:
        events_by_type[event_type.value] = len([e for e in events if e.event_type == event_type])

    events_by_layer = {}
    for layer in TimelineLayer:
        events_by_layer[layer.value] = len([e for e in events if e.layer == layer])

    major_beats = [e for e in events if e.is_major_beat]
    custom_events = [e for e in events if e.is_custom]

    # Chapters with no events
    all_chapters = set(range(chapter_range[0], chapter_range[1] + 1))
    chapters_with_events = set(chapters)
    chapters_with_no_events = sorted(list(all_chapters - chapters_with_events))

    # Chapters with major beats
    chapters_with_major_beats = sorted(list(set(e.chapter_number for e in major_beats)))

    # Character involvement
    character_counts = {}
    for event in events:
        for char_id in event.related_characters:
            character_counts[char_id] = character_counts.get(char_id, 0) + 1

    most_active_characters = [
        {"character_id": char_id, "event_count": count}
        for char_id, count in sorted(character_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # Conflicts
    conflicts = service.get_conflicts(project_id=project_id)
    open_conflicts = [c for c in conflicts if c.status == "open"]

    conflicts_by_severity = {}
    for severity in ConflictSeverity:
        conflicts_by_severity[severity.value] = len([c for c in open_conflicts if c.severity == severity])

    # Pacing score (simple calculation)
    if len(major_beats) > 0:
        ideal_gap = chapter_span / len(major_beats)
        actual_gaps = []
        sorted_beats = sorted(major_beats, key=lambda x: x.chapter_number)
        for i in range(len(sorted_beats) - 1):
            gap = sorted_beats[i + 1].chapter_number - sorted_beats[i].chapter_number
            actual_gaps.append(gap)

        if actual_gaps:
            avg_gap = sum(actual_gaps) / len(actual_gaps)
            # Score based on how close to ideal
            pacing_score = max(0.0, 1.0 - abs(avg_gap - ideal_gap) / ideal_gap)
        else:
            pacing_score = 1.0
    else:
        pacing_score = 0.5

    return TimelineStatisticsResponse(
        total_events=len(events),
        events_by_type=events_by_type,
        events_by_layer=events_by_layer,
        chapter_range=chapter_range,
        major_beats_count=len(major_beats),
        custom_events_count=len(custom_events),
        total_conflicts=len(conflicts),
        open_conflicts=len(open_conflicts),
        conflicts_by_severity=conflicts_by_severity,
        avg_events_per_chapter=len(events) / chapter_span,
        chapters_with_no_events=chapters_with_no_events,
        chapters_with_major_beats=chapters_with_major_beats,
        most_active_characters=most_active_characters,
        pacing_score=pacing_score
    )
