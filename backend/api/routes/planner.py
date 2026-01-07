"""
Planner API Routes

3-level story structure: Book Arc → Chapters → Scenes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database.base import get_db
from services.planner.service import PlannerService
from api.schemas.planner import (
    # Book Arc
    BookArcCreate,
    BookArcUpdate,
    BookArcResponse,
    # Chapter
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    # Scene
    SceneCreate,
    SceneUpdate,
    SceneResponse,
    # Validation
    ValidationResult,
    # Structure
    ProjectStructureResponse,
    ReorderScenesRequest,
)
from api.schemas.canon import MessageResponse

router = APIRouter()


def get_planner_service(db: Session = Depends(get_db)) -> PlannerService:
    """Dependency to get Planner service"""
    return PlannerService(db)


# ===== Book Arc Endpoints =====

@router.post("/arc", response_model=BookArcResponse, status_code=201)
async def create_book_arc(
    data: BookArcCreate,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Create book arc (overall story structure)

    **Book Arc defines:**
    - Premise and theme
    - Three-act structure
    - Story beats (inciting incident, midpoint, climax, etc.)
    - Tension curve across chapters
    """
    try:
        arc = service.create_book_arc(
            project_id=data.project_id,
            data=data.model_dump(exclude={"project_id"}),
        )
        return arc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/arc/{project_id}", response_model=BookArcResponse)
async def get_book_arc(
    project_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """Get book arc for project"""
    arc = service.get_book_arc(project_id)
    if not arc:
        raise HTTPException(status_code=404, detail="Book arc not found")
    return arc


@router.put("/arc/{arc_id}", response_model=BookArcResponse)
async def update_book_arc(
    arc_id: int,
    data: BookArcUpdate,
    service: PlannerService = Depends(get_planner_service),
):
    """Update book arc"""
    try:
        arc = service.update_book_arc(
            arc_id=arc_id,
            data=data.model_dump(exclude_unset=True),
        )
        return arc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/arc/{arc_id}/validate", response_model=ValidationResult)
async def validate_book_arc(
    arc_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Validate book arc structure

    Checks for:
    - Logical act breaks
    - Defined story beats
    - Complete premise and theme
    """
    result = service.validate_book_arc(arc_id)
    return result


# ===== Chapter Endpoints =====

@router.post("/chapter", response_model=ChapterResponse, status_code=201)
async def create_chapter(
    data: ChapterCreate,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Create chapter

    **Chapter defines:**
    - Goal: What must be accomplished
    - Stakes: What's at risk
    - Conflict: What opposes the goal
    - Emotional journey: Opening → closing emotion
    - Active threads and promises
    """
    try:
        chapter = service.create_chapter(
            project_id=data.project_id,
            chapter_number=data.chapter_number,
            data=data.model_dump(exclude={"project_id", "chapter_number"}),
        )
        return chapter
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/chapter/{chapter_id}", response_model=ChapterResponse)
async def get_chapter_by_id(
    chapter_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """Get chapter by ID"""
    chapter = service.get_chapter_by_id(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.get("/chapter", response_model=ChapterResponse)
async def get_chapter(
    project_id: int = Query(...),
    chapter_number: int = Query(..., ge=1),
    service: PlannerService = Depends(get_planner_service),
):
    """Get chapter by project and number"""
    chapter = service.get_chapter(project_id, chapter_number)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.get("/chapters", response_model=List[ChapterResponse])
async def list_chapters(
    project_id: int = Query(...),
    status: Optional[str] = Query(None, description="Filter by status: planned, drafted, revised, final"),
    limit: int = Query(100, ge=1, le=500),
    service: PlannerService = Depends(get_planner_service),
):
    """List all chapters for a project"""
    chapters = service.list_chapters(project_id, status=status, limit=limit)
    return chapters


@router.put("/chapter/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    data: ChapterUpdate,
    service: PlannerService = Depends(get_planner_service),
):
    """Update chapter"""
    try:
        chapter = service.update_chapter(
            chapter_id=chapter_id,
            data=data.model_dump(exclude_unset=True),
        )
        return chapter
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/chapter/{chapter_id}", response_model=MessageResponse)
async def delete_chapter(
    chapter_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """Delete chapter and all its scenes"""
    success = service.delete_chapter(chapter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return MessageResponse(message="Chapter and scenes deleted successfully")


@router.get("/chapter/{chapter_id}/validate", response_model=ValidationResult)
async def validate_chapter(
    chapter_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Validate chapter structure

    Checks for:
    - Defined goal and conflict
    - Emotional journey
    - Reasonable word count
    """
    result = service.validate_chapter(chapter_id)
    return result


# ===== Scene Endpoints =====

@router.post("/scene", response_model=SceneResponse, status_code=201)
async def create_scene(
    data: SceneCreate,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Create scene card

    **Scene card defines:**
    - Goal: What must happen
    - Conflict: What opposes it
    - What changes: Concrete change
    - Participants: Who is present
    - Value shift: Entering → exiting value

    **Used by Draft service** for prose generation
    """
    try:
        scene = service.create_scene(
            chapter_id=data.chapter_id,
            project_id=data.project_id,
            scene_number=data.scene_number,
            data=data.model_dump(exclude={"chapter_id", "project_id", "scene_number"}),
        )
        return scene
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scene/{scene_id}", response_model=SceneResponse)
async def get_scene(
    scene_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """Get scene by ID"""
    scene = service.get_scene(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene


@router.get("/scenes/{chapter_id}", response_model=List[SceneResponse])
async def list_scenes(
    chapter_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """List all scenes for a chapter (in order)"""
    scenes = service.list_scenes(chapter_id)
    return scenes


@router.put("/scene/{scene_id}", response_model=SceneResponse)
async def update_scene(
    scene_id: int,
    data: SceneUpdate,
    service: PlannerService = Depends(get_planner_service),
):
    """Update scene card"""
    try:
        scene = service.update_scene(
            scene_id=scene_id,
            data=data.model_dump(exclude_unset=True),
        )
        return scene
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/scene/{scene_id}", response_model=MessageResponse)
async def delete_scene(
    scene_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """Delete scene"""
    success = service.delete_scene(scene_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scene not found")
    return MessageResponse(message="Scene deleted successfully")


@router.get("/scene/{scene_id}/validate", response_model=ValidationResult)
async def validate_scene(
    scene_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Validate scene card

    Checks for:
    - Defined goal
    - "What changes" specified
    - Participants present
    - Value shift (if applicable)
    """
    result = service.validate_scene(scene_id)
    return result


@router.post("/scenes/reorder", response_model=List[SceneResponse])
async def reorder_scenes(
    chapter_id: int = Query(...),
    data: ReorderScenesRequest = ...,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Reorder scenes within a chapter

    Provide scene IDs in desired order
    """
    try:
        scenes = service.reorder_scenes(chapter_id, data.scene_order)
        return scenes
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Project Structure =====

@router.get("/structure/{project_id}", response_model=ProjectStructureResponse)
async def get_project_structure(
    project_id: int,
    service: PlannerService = Depends(get_planner_service),
):
    """
    Get complete project structure

    Returns:
    - Book arc
    - All chapters
    - Total scenes count
    - Total words
    - Completion metrics
    """
    structure = service.get_project_structure(project_id)
    return structure
