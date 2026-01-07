"""
Canon API Routes

REST endpoints for Canon entity management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database.base import get_db
from services.canon.service import CanonService
from api.schemas.canon import (
    # Character
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    # Location
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    # MagicRule
    MagicRuleCreate,
    MagicRuleUpdate,
    MagicRuleResponse,
    # Event
    EventCreate,
    EventUpdate,
    EventResponse,
    # Promise
    PromiseCreate,
    PromiseUpdate,
    PromiseResponse,
    # Thread
    ThreadCreate,
    ThreadUpdate,
    ThreadResponse,
    # Generic
    CanonEntityResponse,
    CanonVersionResponse,
    ValidationResult,
    EntityStatsResponse,
    MessageResponse,
)

router = APIRouter()


def get_canon_service(db: Session = Depends(get_db)) -> CanonService:
    """Dependency to get Canon service"""
    return CanonService(db)


# ===== Character Endpoints =====

@router.post("/character", response_model=CharacterResponse, status_code=201)
async def create_character(
    data: CharacterCreate,
    commit_message: Optional[str] = Query(None, description="Version commit message"),
    service: CanonService = Depends(get_canon_service),
):
    """
    Create a new character

    Creates character with full psychological profile, behavioral constraints, and voice
    """
    try:
        entity = service.create_entity(
            entity_type="character",
            project_id=data.project_id,
            data=data.model_dump(exclude={"project_id"}),
            commit_message=commit_message,
        )
        return entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/character/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """Get character by ID"""
    entity = service.get_entity("character", character_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Character not found")
    return entity


@router.get("/character", response_model=List[CharacterResponse])
async def list_characters(
    project_id: int = Query(..., description="Project ID"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: CanonService = Depends(get_canon_service),
):
    """List characters for a project"""
    entities = service.list_entities(
        entity_type="character",
        project_id=project_id,
        tags=tags,
        limit=limit,
        offset=offset,
    )
    return entities


@router.put("/character/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    data: CharacterUpdate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Update character"""
    try:
        entity = service.update_entity(
            entity_type="character",
            entity_id=character_id,
            data=data.model_dump(exclude_unset=True),
            commit_message=commit_message,
        )
        return entity
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/character/{character_id}", response_model=MessageResponse)
async def delete_character(
    character_id: int,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Delete character"""
    success = service.delete_entity(
        entity_type="character",
        entity_id=character_id,
        commit_message=commit_message,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    return MessageResponse(message="Character deleted successfully")


# ===== Location Endpoints =====

@router.post("/location", response_model=LocationResponse, status_code=201)
async def create_location(
    data: LocationCreate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Create a new location with rules and restrictions"""
    try:
        entity = service.create_entity(
            entity_type="location",
            project_id=data.project_id,
            data=data.model_dump(exclude={"project_id"}),
            commit_message=commit_message,
        )
        return entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/location/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """Get location by ID"""
    entity = service.get_entity("location", location_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Location not found")
    return entity


@router.get("/location", response_model=List[LocationResponse])
async def list_locations(
    project_id: int = Query(...),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: CanonService = Depends(get_canon_service),
):
    """List locations for a project"""
    entities = service.list_entities(
        entity_type="location",
        project_id=project_id,
        tags=tags,
        limit=limit,
        offset=offset,
    )
    return entities


@router.put("/location/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    data: LocationUpdate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Update location"""
    try:
        entity = service.update_entity(
            entity_type="location",
            entity_id=location_id,
            data=data.model_dump(exclude_unset=True),
            commit_message=commit_message,
        )
        return entity
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/location/{location_id}", response_model=MessageResponse)
async def delete_location(
    location_id: int,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Delete location"""
    success = service.delete_entity(
        entity_type="location",
        entity_id=location_id,
        commit_message=commit_message,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Location not found")
    return MessageResponse(message="Location deleted successfully")


# ===== MagicRule Endpoints =====

@router.post("/magic", response_model=MagicRuleResponse, status_code=201)
async def create_magic_rule(
    data: MagicRuleCreate,
    commit_message: Optional[str] = Query(None, description="Version commit message"),
    service: CanonService = Depends(get_canon_service),
):
    """
    Create a new magic rule or world law

    Magic rules define HARD CONSTRAINTS on your world:
    - Laws that ALWAYS apply
    - Costs and limitations
    - Rare exceptions (must be justified)
    - What is strictly forbidden
    """
    try:
        entity = service.create_entity(
            entity_type="magic_rule",
            project_id=data.project_id,
            data=data.model_dump(exclude={"project_id"}),
            commit_message=commit_message,
        )
        return entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/magic/{magic_id}", response_model=MagicRuleResponse)
async def get_magic_rule(
    magic_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """Get magic rule by ID"""
    entity = service.get_entity("magic_rule", magic_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Magic rule not found")
    return entity


@router.get("/magic", response_model=List[MagicRuleResponse])
async def list_magic_rules(
    project_id: int = Query(..., description="Project ID"),
    rule_type: Optional[str] = Query(None, description="Filter by type: magic, physics, divine, curse, etc."),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: CanonService = Depends(get_canon_service),
):
    """List magic rules for a project"""
    entities = service.list_entities(
        entity_type="magic_rule",
        project_id=project_id,
        tags=tags,
        limit=limit,
        offset=offset,
    )

    # Filter by rule type if provided
    if rule_type:
        entities = [e for e in entities if e.rule_type == rule_type]

    return entities


@router.put("/magic/{magic_id}", response_model=MagicRuleResponse)
async def update_magic_rule(
    magic_id: int,
    data: MagicRuleUpdate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Update magic rule"""
    try:
        entity = service.update_entity(
            entity_type="magic_rule",
            entity_id=magic_id,
            data=data.model_dump(exclude_unset=True),
            commit_message=commit_message,
        )
        return entity
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/magic/{magic_id}", response_model=MessageResponse)
async def delete_magic_rule(
    magic_id: int,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Delete magic rule"""
    success = service.delete_entity(
        entity_type="magic_rule",
        entity_id=magic_id,
        commit_message=commit_message,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Magic rule not found")
    return MessageResponse(message="Magic rule deleted successfully")


# ===== Promise Endpoints =====

@router.post("/promise", response_model=PromiseResponse, status_code=201)
async def create_promise(
    data: PromiseCreate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """
    Create a narrative promise

    Promises track setup/payoff pairs to ensure narrative consistency
    """
    try:
        entity = service.create_entity(
            entity_type="promise",
            project_id=data.project_id,
            data=data.model_dump(exclude={"project_id"}),
            commit_message=commit_message,
        )
        return entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/promise/{promise_id}", response_model=PromiseResponse)
async def get_promise(
    promise_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """Get promise by ID"""
    entity = service.get_entity("promise", promise_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Promise not found")
    return entity


@router.get("/promise", response_model=List[PromiseResponse])
async def list_promises(
    project_id: int = Query(...),
    status: Optional[str] = Query(None, description="Filter by status: open, fulfilled, abandoned"),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: CanonService = Depends(get_canon_service),
):
    """
    List promises for a project

    Useful for tracking unfulfilled promises and ensuring payoffs
    """
    entities = service.list_entities(
        entity_type="promise",
        project_id=project_id,
        tags=tags,
        limit=limit,
        offset=offset,
    )

    # Filter by status if provided
    if status:
        entities = [e for e in entities if e.status == status]

    return entities


@router.put("/promise/{promise_id}", response_model=PromiseResponse)
async def update_promise(
    promise_id: int,
    data: PromiseUpdate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Update promise (e.g., mark as fulfilled with payoff details)"""
    try:
        entity = service.update_entity(
            entity_type="promise",
            entity_id=promise_id,
            data=data.model_dump(exclude_unset=True),
            commit_message=commit_message,
        )
        return entity
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/promise/{promise_id}", response_model=MessageResponse)
async def delete_promise(
    promise_id: int,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Delete promise"""
    success = service.delete_entity(
        entity_type="promise",
        entity_id=promise_id,
        commit_message=commit_message,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Promise not found")
    return MessageResponse(message="Promise deleted successfully")


# ===== Thread Endpoints =====

@router.post("/thread", response_model=ThreadResponse, status_code=201)
async def create_thread(
    data: ThreadCreate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """
    Create a narrative thread

    Threads represent subplots, character arcs, or mysteries spanning multiple chapters
    """
    try:
        entity = service.create_entity(
            entity_type="thread",
            project_id=data.project_id,
            data=data.model_dump(exclude={"project_id"}),
            commit_message=commit_message,
        )
        return entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/thread/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """Get thread by ID"""
    entity = service.get_entity("thread", thread_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Thread not found")
    return entity


@router.get("/thread", response_model=List[ThreadResponse])
async def list_threads(
    project_id: int = Query(...),
    status: Optional[str] = Query(None, description="Filter by status: active, resolved, abandoned"),
    thread_type: Optional[str] = Query(None, description="Filter by type"),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: CanonService = Depends(get_canon_service),
):
    """List threads for a project"""
    entities = service.list_entities(
        entity_type="thread",
        project_id=project_id,
        tags=tags,
        limit=limit,
        offset=offset,
    )

    # Filter by status
    if status:
        entities = [e for e in entities if e.status == status]

    # Filter by type
    if thread_type:
        entities = [e for e in entities if e.thread_type == thread_type]

    return entities


@router.put("/thread/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: int,
    data: ThreadUpdate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Update thread (e.g., progress to next chapter, adjust tension)"""
    try:
        entity = service.update_entity(
            entity_type="thread",
            entity_id=thread_id,
            data=data.model_dump(exclude_unset=True),
            commit_message=commit_message,
        )
        return entity
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/thread/{thread_id}", response_model=MessageResponse)
async def delete_thread(
    thread_id: int,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Delete thread"""
    success = service.delete_entity(
        entity_type="thread",
        entity_id=thread_id,
        commit_message=commit_message,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return MessageResponse(message="Thread deleted successfully")


# ===== Event (Timeline) Endpoints =====

@router.post("/event", response_model=EventResponse, status_code=201)
async def create_event(
    data: EventCreate,
    commit_message: Optional[str] = Query(None, description="Version commit message"),
    service: CanonService = Depends(get_canon_service),
):
    """
    Create a timeline event

    Events track significant moments in your story timeline:
    - Plot events, backstory, world events, character moments
    - Causal relationships (causes/effects)
    - Consequences and long-term impacts
    - Participants and locations
    """
    try:
        entity = service.create_entity(
            entity_type="event",
            project_id=data.project_id,
            data=data.model_dump(exclude={"project_id"}),
            commit_message=commit_message,
        )
        return entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/event/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """Get event by ID"""
    entity = service.get_entity("event", event_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Event not found")
    return entity


@router.get("/event", response_model=List[EventResponse])
async def list_events(
    project_id: int = Query(..., description="Project ID"),
    chapter_number: Optional[int] = Query(None, description="Filter by chapter"),
    location_id: Optional[int] = Query(None, description="Filter by location"),
    impact_level_min: Optional[int] = Query(None, ge=0, le=100, description="Min impact level"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: CanonService = Depends(get_canon_service),
):
    """
    List events for a project

    Events are returned in chronological order by chapter/scene
    """
    entities = service.list_entities(
        entity_type="event",
        project_id=project_id,
        tags=tags,
        limit=limit,
        offset=offset,
    )

    # Filter by chapter
    if chapter_number is not None:
        entities = [e for e in entities if e.chapter_number == chapter_number]

    # Filter by location
    if location_id is not None:
        entities = [e for e in entities if e.location_id == location_id]

    # Filter by impact level
    if impact_level_min is not None:
        entities = [e for e in entities if e.impact_level >= impact_level_min]

    # Sort chronologically
    entities.sort(key=lambda e: (e.chapter_number or 0, e.scene_number or 0))

    return entities


@router.put("/event/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    data: EventUpdate,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Update event"""
    try:
        entity = service.update_entity(
            entity_type="event",
            entity_id=event_id,
            data=data.model_dump(exclude_unset=True),
            commit_message=commit_message,
        )
        return entity
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/event/{event_id}", response_model=MessageResponse)
async def delete_event(
    event_id: int,
    commit_message: Optional[str] = Query(None),
    service: CanonService = Depends(get_canon_service),
):
    """Delete event"""
    success = service.delete_entity(
        entity_type="event",
        entity_id=event_id,
        commit_message=commit_message,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return MessageResponse(message="Event deleted successfully")


# ===== Validation Endpoints =====

@router.get("/validate/{entity_type}/{entity_id}", response_model=ValidationResult)
async def validate_entity(
    entity_type: str,
    entity_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """
    Validate a canon entity

    Checks for missing fields, broken relationships, and inconsistencies
    """
    try:
        result = service.validate_entity(entity_type, entity_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Version Endpoints =====

@router.get("/versions/{project_id}", response_model=List[CanonVersionResponse])
async def get_version_history(
    project_id: int,
    limit: int = Query(50, ge=1, le=200),
    service: CanonService = Depends(get_canon_service),
):
    """
    Get canon version history for a project

    Returns git-like commit history of all changes to canon
    """
    versions = service.get_version_history(project_id, limit=limit)
    return versions


@router.get("/version/{version_id}", response_model=CanonVersionResponse)
async def get_version(
    version_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """Get specific canon version"""
    version = service.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


# ===== Statistics Endpoints =====

@router.get("/stats/{project_id}", response_model=EntityStatsResponse)
async def get_entity_stats(
    project_id: int,
    service: CanonService = Depends(get_canon_service),
):
    """
    Get canon entity statistics

    Returns counts of all entity types in a project
    """
    stats = service.get_entity_stats(project_id)
    stats["total"] = sum(stats.values())
    return stats
