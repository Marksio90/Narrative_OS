"""
Consequence Simulator API Routes

REST endpoints for event tracking and consequence prediction
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional

from core.database.base import get_db
from services.ai.consequence_engine import ConsequenceEngine
from core.models.consequences import (
    StoryEvent,
    Consequence,
    EventEntity,
    ConsequenceStatus,
    ConsequenceTimeframe,
    EventType
)
from api.schemas.consequences import (
    AnalyzeSceneRequest,
    PredictConsequencesRequest,
    MarkConsequenceRequest,
    CreateEventRequest,
    StoryEventResponse,
    ConsequenceResponse,
    EventWithConsequencesResponse,
    ConsequenceGraphResponse,
    ActiveConsequencesResponse,
    AnalyzeSceneResponse,
    ConsequenceStatsResponse,
)

router = APIRouter()


def get_consequence_engine(db: Session = Depends(get_db)) -> ConsequenceEngine:
    """Dependency to get Consequence Engine"""
    return ConsequenceEngine(db)


# ===== Event Endpoints =====

@router.post("/analyze-scene", response_model=AnalyzeSceneResponse)
async def analyze_scene(
    data: AnalyzeSceneRequest,
    engine: ConsequenceEngine = Depends(get_consequence_engine),
):
    """
    Analyze a scene and extract significant events

    Uses AI to identify important story moments and predict their consequences.
    Automatically creates StoryEvent records and predicts consequences.
    """
    try:
        # Extract events from scene
        events = await engine.extract_events_from_scene(
            project_id=data.project_id,
            scene_id=data.scene_id,
            scene_text=data.scene_text,
            chapter_number=data.chapter_number
        )

        # Predict consequences for each event
        total_consequences = 0
        for event in events:
            consequences = await engine.predict_consequences(event)
            total_consequences += len(consequences)

        return AnalyzeSceneResponse(
            success=True,
            events_extracted=len(events),
            events=[StoryEventResponse.model_validate(e) for e in events],
            consequences_predicted=total_consequences,
            message=f"Extracted {len(events)} events and predicted {total_consequences} consequences"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scene analysis failed: {str(e)}")


@router.post("/events", response_model=StoryEventResponse, status_code=201)
async def create_event(
    data: CreateEventRequest,
    db: Session = Depends(get_db),
):
    """
    Manually create a story event

    Useful when AI extraction misses important events or for
    manual event tracking.
    """
    try:
        event = StoryEvent(
            project_id=data.project_id,
            scene_id=data.scene_id,
            chapter_number=data.chapter_number,
            title=data.title,
            description=data.description,
            event_type=EventType(data.event_type),
            magnitude=data.magnitude,
            emotional_impact=data.emotional_impact,
            causes=[],
            effects=[]
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        # Add entity relationships
        for char_id in data.affected_character_ids:
            entity = EventEntity(
                event_id=event.id,
                entity_type='character',
                entity_id=char_id
            )
            db.add(entity)

        for loc_id in data.affected_location_ids:
            entity = EventEntity(
                event_id=event.id,
                entity_type='location',
                entity_id=loc_id
            )
            db.add(entity)

        for thread_id in data.affected_thread_ids:
            entity = EventEntity(
                event_id=event.id,
                entity_type='thread',
                entity_id=thread_id
            )
            db.add(entity)

        if data.affected_character_ids or data.affected_location_ids or data.affected_thread_ids:
            db.commit()

        return StoryEventResponse.model_validate(event)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid event type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event creation failed: {str(e)}")


@router.get("/events/{event_id}", response_model=EventWithConsequencesResponse)
async def get_event_with_consequences(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    Get event details with all its consequences
    """
    event = db.execute(
        select(StoryEvent).where(StoryEvent.id == event_id)
    ).scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get consequences
    consequences = db.execute(
        select(Consequence).where(Consequence.source_event_id == event_id)
    ).scalars().all()

    active_count = sum(
        1 for c in consequences
        if c.status in [ConsequenceStatus.POTENTIAL, ConsequenceStatus.ACTIVE]
    )

    return EventWithConsequencesResponse(
        event=StoryEventResponse.model_validate(event),
        consequences=[ConsequenceResponse.model_validate(c) for c in consequences],
        consequence_count=len(consequences),
        active_consequence_count=active_count
    )


@router.get("/events", response_model=List[StoryEventResponse])
async def list_events(
    project_id: int = Query(..., description="Project ID"),
    chapter_number: Optional[int] = Query(None, description="Filter by chapter"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List events for a project

    Supports filtering by chapter and event type.
    """
    query = select(StoryEvent).where(StoryEvent.project_id == project_id)

    if chapter_number is not None:
        query = query.where(StoryEvent.chapter_number == chapter_number)

    if event_type:
        try:
            query = query.where(StoryEvent.event_type == EventType(event_type))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")

    query = query.order_by(StoryEvent.chapter_number, StoryEvent.id).limit(limit).offset(offset)

    events = db.execute(query).scalars().all()
    return [StoryEventResponse.model_validate(e) for e in events]


# ===== Consequence Endpoints =====

@router.post("/events/{event_id}/predict-consequences", response_model=List[ConsequenceResponse])
async def predict_consequences(
    event_id: int,
    data: Optional[PredictConsequencesRequest] = None,
    engine: ConsequenceEngine = Depends(get_consequence_engine),
    db: Session = Depends(get_db),
):
    """
    Predict consequences for an event using AI

    Analyzes the event and generates likely consequences with
    probability, severity, and timeframe estimates.
    """
    event = db.execute(
        select(StoryEvent).where(StoryEvent.id == event_id)
    ).scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        context = data.context if data else None
        consequences = await engine.predict_consequences(event, context)
        return [ConsequenceResponse.model_validate(c) for c in consequences]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.put("/consequences/{consequence_id}/status", response_model=ConsequenceResponse)
async def update_consequence_status(
    consequence_id: int,
    data: MarkConsequenceRequest,
    db: Session = Depends(get_db),
):
    """
    Update consequence status

    Mark a consequence as active, realized, or invalidated.
    """
    consequence = db.execute(
        select(Consequence).where(Consequence.id == consequence_id)
    ).scalar_one_or_none()

    if not consequence:
        raise HTTPException(status_code=404, detail="Consequence not found")

    try:
        from datetime import datetime

        status = ConsequenceStatus(data.status)
        consequence.status = status

        if status == ConsequenceStatus.REALIZED:
            consequence.realized_at = datetime.utcnow()
            if data.target_event_id:
                consequence.target_event_id = data.target_event_id

        elif status == ConsequenceStatus.INVALIDATED:
            consequence.invalidated_at = datetime.utcnow()
            consequence.invalidation_reason = data.invalidation_reason

        db.commit()
        db.refresh(consequence)

        return ConsequenceResponse.model_validate(consequence)

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {data.status}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.get("/consequences/active", response_model=ActiveConsequencesResponse)
async def get_active_consequences(
    project_id: int = Query(..., description="Project ID"),
    chapter_number: Optional[int] = Query(None, description="Current chapter number"),
    engine: ConsequenceEngine = Depends(get_consequence_engine),
):
    """
    Get active consequences for a project

    Returns consequences that are still potential or active,
    useful for showing what might happen next in the story.
    """
    try:
        consequences = await engine.get_active_consequences(project_id, chapter_number)

        high_prob = sum(1 for c in consequences if c.probability > 0.7)
        high_sev = sum(1 for c in consequences if c.severity > 0.7)

        return ActiveConsequencesResponse(
            consequences=[ConsequenceResponse.model_validate(c) for c in consequences],
            total_count=len(consequences),
            high_probability_count=high_prob,
            high_severity_count=high_sev
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


# ===== Graph Endpoints =====

@router.get("/graph", response_model=ConsequenceGraphResponse)
async def get_consequence_graph(
    project_id: int = Query(..., description="Project ID"),
    start_chapter: Optional[int] = Query(None, description="Start chapter (inclusive)"),
    end_chapter: Optional[int] = Query(None, description="End chapter (inclusive)"),
    engine: ConsequenceEngine = Depends(get_consequence_engine),
):
    """
    Build consequence graph for visualization

    Returns events, consequences, and connections in a format
    suitable for graph visualization libraries like React Flow.
    """
    try:
        chapter_range = None
        if start_chapter is not None and end_chapter is not None:
            chapter_range = (start_chapter, end_chapter)

        graph = await engine.build_consequence_graph(project_id, chapter_range)

        active_count = sum(
            1 for c in graph.consequences
            if c['status'] in ['potential', 'active']
        )

        return ConsequenceGraphResponse(
            events=graph.events,
            consequences=graph.consequences,
            connections=graph.connections,
            total_events=len(graph.events),
            total_consequences=len(graph.consequences),
            active_consequences=active_count
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph building failed: {str(e)}")


# ===== Statistics Endpoints =====

@router.get("/stats", response_model=ConsequenceStatsResponse)
async def get_consequence_stats(
    project_id: int = Query(..., description="Project ID"),
    db: Session = Depends(get_db),
):
    """
    Get statistics about consequences for a project

    Useful for dashboards and analytics.
    """
    # Count events
    total_events = db.execute(
        select(func.count(StoryEvent.id)).where(StoryEvent.project_id == project_id)
    ).scalar()

    # Count consequences by status
    consequences = db.execute(
        select(Consequence).join(StoryEvent).where(StoryEvent.project_id == project_id)
    ).scalars().all()

    total_consequences = len(consequences)
    potential = sum(1 for c in consequences if c.status == ConsequenceStatus.POTENTIAL)
    active = sum(1 for c in consequences if c.status == ConsequenceStatus.ACTIVE)
    realized = sum(1 for c in consequences if c.status == ConsequenceStatus.REALIZED)
    invalidated = sum(1 for c in consequences if c.status == ConsequenceStatus.INVALIDATED)

    # Events by type
    events_by_type = db.execute(
        select(StoryEvent.event_type, func.count(StoryEvent.id))
        .where(StoryEvent.project_id == project_id)
        .group_by(StoryEvent.event_type)
    ).all()

    events_by_type_dict = {et.value: count for et, count in events_by_type}

    # Consequences by timeframe
    cons_by_timeframe = {}
    for c in consequences:
        timeframe = c.timeframe.value
        cons_by_timeframe[timeframe] = cons_by_timeframe.get(timeframe, 0) + 1

    avg_per_event = total_consequences / total_events if total_events > 0 else 0

    return ConsequenceStatsResponse(
        total_events=total_events,
        total_consequences=total_consequences,
        potential_consequences=potential,
        active_consequences=active,
        realized_consequences=realized,
        invalidated_consequences=invalidated,
        avg_consequences_per_event=avg_per_event,
        events_by_type=events_by_type_dict,
        consequences_by_timeframe=cons_by_timeframe
    )
