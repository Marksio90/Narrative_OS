"""
Character Arc Tracker API Routes

RESTful endpoints for character arc management and analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import anthropic

from core.database.base import get_db
from core.models.character_arcs import ArcType, MilestoneType, GoalStatus
from core.models.canon import Character
from services.ai.character_arc_service import CharacterArcService
from api.schemas.character_arcs import (
    # Requests
    CreateArcRequest,
    UpdateArcProgressRequest,
    AddMilestoneRequest,
    TrackEmotionalStateRequest,
    CreateGoalRequest,
    UpdateGoalProgressRequest,
    TrackRelationshipChangeRequest,
    AnalyzeSceneForMilestoneRequest,
    ExtractEmotionalStateRequest,
    # Responses
    ArcResponse,
    MilestoneResponse,
    EmotionalStateResponse,
    GoalProgressResponse,
    RelationshipEvolutionResponse,
    ArcWithMilestonesResponse,
    CharacterArcSummaryResponse,
    EmotionalJourneyResponse,
    ArcHealthAnalysisResponse,
    ArcReportResponse,
    GoalSummaryResponse,
    RelationshipTimelineResponse,
)

router = APIRouter()


def get_arc_service(db: Session = Depends(get_db)) -> CharacterArcService:
    """Dependency to get character arc service"""
    client = anthropic.Anthropic()
    return CharacterArcService(db=db, anthropic_client=client)


# ==================== Arc CRUD ====================

@router.post("/arcs", response_model=ArcResponse, status_code=201)
async def create_arc(
    request: CreateArcRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """
    Create a new character arc

    Tracks a character's development journey across the story
    """
    try:
        arc_type = ArcType(request.arc_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid arc type: {request.arc_type}"
        )

    arc = service.create_arc(
        project_id=request.project_id,
        character_id=request.character_id,
        arc_type=arc_type,
        name=request.name,
        description=request.description,
        start_chapter=request.start_chapter,
        end_chapter=request.end_chapter,
        starting_state=request.starting_state,
        ending_state=request.ending_state,
    )

    return arc


@router.get("/arcs/{arc_id}", response_model=ArcWithMilestonesResponse)
async def get_arc(
    arc_id: int,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Get arc by ID with its milestones"""
    arc = service.get_arc(arc_id)
    if not arc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arc {arc_id} not found"
        )

    milestones = service.get_arc_milestones(arc_id)

    return {
        "arc": arc,
        "milestones": milestones,
        "milestone_count": len(milestones),
        "achieved_count": sum(1 for m in milestones if m.is_achieved),
    }


@router.get("/arcs", response_model=List[ArcResponse])
async def get_arcs(
    project_id: int,
    character_id: Optional[int] = None,
    active_only: bool = False,
    service: CharacterArcService = Depends(get_arc_service),
):
    """
    Get arcs for project or character

    Query params:
    - project_id: Required
    - character_id: Optional, filter by character
    - active_only: Only return incomplete arcs
    """
    arcs = service.get_character_arcs(
        project_id=project_id,
        character_id=character_id,
        active_only=active_only,
    )

    return arcs


@router.get("/characters/{character_id}/arcs", response_model=CharacterArcSummaryResponse)
async def get_character_arc_summary(
    character_id: int,
    db: Session = Depends(get_db),
    service: CharacterArcService = Depends(get_arc_service),
):
    """Get summary of all arcs for a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )

    arcs = service.get_character_arcs(
        project_id=character.project_id,
        character_id=character_id,
        active_only=False,
    )

    return {
        "character_id": character_id,
        "character_name": character.name,
        "total_arcs": len(arcs),
        "active_arcs": sum(1 for a in arcs if not a.is_complete),
        "completed_arcs": sum(1 for a in arcs if a.is_complete),
        "arcs": arcs,
    }


@router.put("/arcs/{arc_id}/progress", response_model=ArcResponse)
async def update_arc_progress(
    arc_id: int,
    request: UpdateArcProgressRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Update arc progress"""
    try:
        arc = service.update_arc_progress(
            arc_id=arc_id,
            current_chapter=request.current_chapter,
            completion_percentage=request.completion_percentage,
        )
        return arc
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== Milestones ====================

@router.post("/milestones", response_model=MilestoneResponse, status_code=201)
async def add_milestone(
    request: AddMilestoneRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Add milestone to arc"""
    try:
        milestone_type = MilestoneType(request.milestone_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid milestone type: {request.milestone_type}"
        )

    try:
        milestone = service.add_milestone(
            arc_id=request.arc_id,
            chapter_number=request.chapter_number,
            milestone_type=milestone_type,
            title=request.title,
            description=request.description,
            emotional_impact=request.emotional_impact,
            character_change=request.character_change,
            story_event_id=request.story_event_id,
        )
        return milestone
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/arcs/{arc_id}/milestones", response_model=List[MilestoneResponse])
async def get_arc_milestones(
    arc_id: int,
    include_unachieved: bool = True,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Get milestones for an arc"""
    milestones = service.get_arc_milestones(
        arc_id=arc_id,
        include_unachieved=include_unachieved,
    )
    return milestones


# ==================== Emotional States ====================

@router.post("/emotional-states", response_model=EmotionalStateResponse, status_code=201)
async def track_emotional_state(
    request: TrackEmotionalStateRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Track emotional state for a chapter"""
    try:
        state = service.track_emotional_state(
            character_id=request.character_id,
            chapter_number=request.chapter_number,
            dominant_emotion=request.dominant_emotion,
            intensity=request.intensity,
            valence=request.valence,
            arc_id=request.arc_id,
            secondary_emotions=request.secondary_emotions,
            triggers=request.triggers,
            mental_state=request.mental_state,
            stress_level=request.stress_level,
            confidence_level=request.confidence_level,
        )
        return state
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/characters/{character_id}/emotional-journey", response_model=EmotionalJourneyResponse)
async def get_emotional_journey(
    character_id: int,
    start_chapter: Optional[int] = None,
    end_chapter: Optional[int] = None,
    db: Session = Depends(get_db),
    service: CharacterArcService = Depends(get_arc_service),
):
    """Get character's emotional journey across chapters"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )

    states = service.get_emotional_journey(
        character_id=character_id,
        start_chapter=start_chapter,
        end_chapter=end_chapter,
    )

    # Calculate summary stats
    dominant_emotions = {}
    for state in states:
        if state.dominant_emotion:
            dominant_emotions[state.dominant_emotion] = dominant_emotions.get(state.dominant_emotion, 0) + 1

    intensities = [s.intensity for s in states if s.intensity is not None]
    intensity_avg = sum(intensities) / len(intensities) if intensities else 0

    valences = [s.valence for s in states if s.valence is not None]
    if len(valences) >= 3:
        first_third = sum(valences[:len(valences)//3]) / (len(valences)//3)
        last_third = sum(valences[-(len(valences)//3):]) / (len(valences)//3)
        diff = last_third - first_third
        if diff > 0.2:
            valence_trend = 'improving'
        elif diff < -0.2:
            valence_trend = 'declining'
        else:
            valence_trend = 'stable'
    else:
        valence_trend = 'insufficient_data'

    return {
        "character_id": character_id,
        "character_name": character.name,
        "start_chapter": start_chapter or (states[0].chapter_number if states else 1),
        "end_chapter": end_chapter or (states[-1].chapter_number if states else 1),
        "states": states,
        "dominant_emotions": dominant_emotions,
        "intensity_average": intensity_avg,
        "valence_trend": valence_trend,
    }


# ==================== Goal Progress ====================

@router.post("/goals", response_model=GoalProgressResponse, status_code=201)
async def create_goal(
    request: CreateGoalRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Create a character goal to track"""
    try:
        goal = service.create_goal(
            character_id=request.character_id,
            goal_description=request.goal_description,
            chapter_number=request.chapter_number,
            goal_type=request.goal_type,
            priority=request.priority,
            stakes=request.stakes,
            arc_id=request.arc_id,
        )
        return goal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/goals/{goal_id}/progress", response_model=GoalProgressResponse)
async def update_goal_progress(
    goal_id: int,
    request: UpdateGoalProgressRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Update goal progress"""
    try:
        goal = service.update_goal_progress(
            goal_id=goal_id,
            chapter_number=request.chapter_number,
            progress_percentage=request.progress_percentage,
            obstacle=request.obstacle,
            victory=request.victory,
            setback=request.setback,
        )
        return goal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/characters/{character_id}/goals", response_model=GoalSummaryResponse)
async def get_character_goals(
    character_id: int,
    active_only: bool = False,
    db: Session = Depends(get_db),
    service: CharacterArcService = Depends(get_arc_service),
):
    """Get all goals for a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )

    goals = service.get_character_goals(
        character_id=character_id,
        active_only=active_only,
    )

    return {
        "character_id": character_id,
        "character_name": character.name,
        "total_goals": len(goals),
        "active_goals": sum(1 for g in goals if g.status in [GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS]),
        "achieved_goals": sum(1 for g in goals if g.status == GoalStatus.ACHIEVED),
        "failed_goals": sum(1 for g in goals if g.status == GoalStatus.FAILED),
        "goals": goals,
    }


# ==================== Relationship Evolution ====================

@router.post("/relationships", response_model=RelationshipEvolutionResponse, status_code=201)
async def track_relationship_change(
    request: TrackRelationshipChangeRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """Track how a relationship changes"""
    try:
        rel_evolution = service.track_relationship_change(
            character_id=request.character_id,
            related_character_id=request.related_character_id,
            chapter_number=request.chapter_number,
            relationship_type=request.relationship_type,
            relationship_strength=request.relationship_strength,
            trust_level=request.trust_level,
            affection_level=request.affection_level,
            respect_level=request.respect_level,
            conflict_level=request.conflict_level,
            key_moment=request.key_moment,
        )
        return rel_evolution
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/relationships/{character_id}/{related_character_id}", response_model=RelationshipTimelineResponse)
async def get_relationship_evolution(
    character_id: int,
    related_character_id: int,
    start_chapter: Optional[int] = None,
    end_chapter: Optional[int] = None,
    db: Session = Depends(get_db),
    service: CharacterArcService = Depends(get_arc_service),
):
    """Get relationship evolution over time"""
    character = db.query(Character).filter(Character.id == character_id).first()
    related_character = db.query(Character).filter(Character.id == related_character_id).first()

    if not character or not related_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    evolution = service.get_relationship_evolution(
        character_id=character_id,
        related_character_id=related_character_id,
        start_chapter=start_chapter,
        end_chapter=end_chapter,
    )

    # Find key turning points (big strength changes)
    turning_points = []
    for i in range(1, len(evolution)):
        prev = evolution[i-1]
        curr = evolution[i]
        if prev.relationship_strength is not None and curr.relationship_strength is not None:
            change = abs(curr.relationship_strength - prev.relationship_strength)
            if change > 0.3:  # Significant change
                turning_points.append({
                    "chapter": curr.chapter_number,
                    "change": curr.relationship_strength - prev.relationship_strength,
                    "event": curr.key_moments[-1] if curr.key_moments else None,
                })

    return {
        "character_id": character_id,
        "related_character_id": related_character_id,
        "character_name": character.name,
        "related_character_name": related_character.name,
        "evolution": evolution,
        "start_state": evolution[0] if evolution else None,
        "current_state": evolution[-1] if evolution else None,
        "trajectory": evolution[-1].trajectory if evolution and evolution[-1].trajectory else 'unknown',
        "key_turning_points": turning_points,
    }


# ==================== AI Analysis Endpoints ====================

@router.post("/arcs/{arc_id}/analyze-health", response_model=ArcHealthAnalysisResponse)
async def analyze_arc_health(
    arc_id: int,
    service: CharacterArcService = Depends(get_arc_service),
):
    """
    Use AI to analyze arc health

    Returns pacing, consistency scores and suggestions
    """
    try:
        analysis = await service.analyze_arc_health(arc_id)
        return analysis
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/arcs/{arc_id}/detect-milestone", response_model=Optional[MilestoneResponse])
async def detect_milestone_from_scene(
    arc_id: int,
    request: AnalyzeSceneForMilestoneRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """
    Analyze scene to detect if it contains a character milestone

    Uses AI to identify character development moments
    """
    try:
        milestone = await service.detect_milestone_from_scene(
            arc_id=request.arc_id,
            scene_text=request.scene_text,
            chapter_number=request.chapter_number,
            story_event_id=request.story_event_id,
        )
        return milestone
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/characters/{character_id}/extract-emotional-state", response_model=Optional[EmotionalStateResponse])
async def extract_emotional_state(
    character_id: int,
    request: ExtractEmotionalStateRequest,
    service: CharacterArcService = Depends(get_arc_service),
):
    """
    Extract emotional state from scene using AI

    Analyzes prose to determine character's emotional state
    """
    emotional_state = await service.extract_emotional_state_from_scene(
        character_id=request.character_id,
        chapter_number=request.chapter_number,
        scene_text=request.scene_text,
        arc_id=request.arc_id,
    )

    return emotional_state


@router.get("/arcs/{arc_id}/report", response_model=ArcReportResponse)
async def generate_arc_report(
    arc_id: int,
    service: CharacterArcService = Depends(get_arc_service),
):
    """
    Generate comprehensive arc analysis report

    Includes health analysis, milestones, emotional journey, and goals
    """
    try:
        report = await service.generate_arc_report(arc_id)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
