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
