"""
AI Draft Generation API Routes
Advanced AI-powered prose generation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from core.database.base import get_db
from core.auth.config import current_active_user
from core.auth.permissions import require_project_access
from core.models.user import User, CollaboratorRole
from services.ai import DraftService, AIConfig, GENERATION_PRESETS, get_preset


router = APIRouter()


# Request/Response Models
class SceneGenerationRequest(BaseModel):
    """Request to generate a scene"""
    scene_description: str = Field(..., description="What should happen in this scene")
    act_number: Optional[int] = Field(None, ge=1, le=5, description="Act number (1-5)")
    chapter_number: Optional[int] = Field(None, ge=1, description="Chapter number")
    pov_character_id: Optional[int] = Field(None, description="POV character ID")
    previous_scene_ids: Optional[List[int]] = Field(None, description="Recent scenes for continuity")
    target_word_count: int = Field(1000, ge=100, le=5000, description="Target word count")
    style_reference: Optional[str] = Field(None, description="Sample text to match style")
    preset: str = Field("balanced", description="Generation preset (fast_draft, balanced, premium)")


class BeatsExpansionRequest(BaseModel):
    """Request to expand story beats"""
    beats: List[str] = Field(..., description="Story beats to expand")
    pov_character_id: Optional[int] = Field(None)
    words_per_beat: int = Field(200, ge=50, le=1000)
    preset: str = Field("balanced")


class ContinuationRequest(BaseModel):
    """Request to continue from existing text"""
    existing_text: str = Field(..., description="Text to continue from")
    continuation_prompt: str = Field(..., description="What happens next")
    target_word_count: int = Field(500, ge=100, le=2000)
    preset: str = Field("balanced")


class RefinementRequest(BaseModel):
    """Request to refine prose"""
    prose: str = Field(..., description="Prose to refine")
    refinement_goals: List[str] = Field(..., description="What to improve")
    preserve_length: bool = Field(True, description="Keep similar word count")
    preset: str = Field("balanced")


class GenerationResponse(BaseModel):
    """Response from generation"""
    text: str
    model_used: str
    tokens_used: int
    cost: float
    quality_score: float
    refinement_iterations: int
    metadata: dict
    timestamp: str


def get_draft_service(
    preset: str,
    db: Session = Depends(get_db)
) -> DraftService:
    """Get Draft Service with specified preset"""
    config = get_preset(preset)
    return DraftService(db=db, config=config)


@router.post("/projects/{project_id}/ai/generate-scene", response_model=GenerationResponse)
async def generate_scene(
    project_id: int,
    request: SceneGenerationRequest,
    user: User = Depends(require_project_access(min_role=CollaboratorRole.WRITER)),
    db: Session = Depends(get_db)
):
    """
    Generate a complete scene using AI

    Requires WRITER access or higher.

    Uses multi-agent AI collaboration:
    1. Planner agent outlines scene structure
    2. Writer agent generates initial prose
    3. Critic agent provides feedback
    4. Editor agent refines based on critique
    5. Canon Keeper verifies consistency

    Features:
    - Canon-aware generation (RAG)
    - Character voice consistency
    - Iterative refinement (up to 3 passes)
    - Style matching
    - Promise/payoff tracking
    """
    service = get_draft_service(request.preset, db)

    try:
        result = await service.generate_scene(
            project_id=project_id,
            scene_description=request.scene_description,
            act_number=request.act_number,
            chapter_number=request.chapter_number,
            pov_character_id=request.pov_character_id,
            previous_scene_ids=request.previous_scene_ids,
            target_word_count=request.target_word_count,
            style_reference=request.style_reference
        )

        return GenerationResponse(
            text=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            cost=result.cost,
            quality_score=result.quality_score,
            refinement_iterations=result.refinement_iterations,
            metadata=result.metadata,
            timestamp=result.timestamp.isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/projects/{project_id}/ai/expand-beats", response_model=List[GenerationResponse])
async def expand_beats(
    project_id: int,
    request: BeatsExpansionRequest,
    user: User = Depends(require_project_access(min_role=CollaboratorRole.WRITER)),
    db: Session = Depends(get_db)
):
    """
    Expand story beats into full prose

    Takes a list of beat descriptions and generates prose for each.
    Each beat uses context from previous beats for continuity.

    Example beats:
    - "Sarah discovers the hidden door behind the bookshelf"
    - "She enters the dark passage, hearing strange sounds"
    - "At the end, she finds the ancient artifact"
    """
    service = get_draft_service(request.preset, db)

    try:
        results = await service.expand_beats(
            project_id=project_id,
            beats=request.beats,
            pov_character_id=request.pov_character_id,
            words_per_beat=request.words_per_beat
        )

        return [
            GenerationResponse(
                text=r.text,
                model_used=r.model_used,
                tokens_used=r.tokens_used,
                cost=r.cost,
                quality_score=r.quality_score,
                refinement_iterations=r.refinement_iterations,
                metadata=r.metadata,
                timestamp=r.timestamp.isoformat()
            )
            for r in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Beat expansion failed: {str(e)}"
        )


@router.post("/projects/{project_id}/ai/continue", response_model=GenerationResponse)
async def continue_from_text(
    project_id: int,
    request: ContinuationRequest,
    user: User = Depends(require_project_access(min_role=CollaboratorRole.WRITER)),
    db: Session = Depends(get_db)
):
    """
    Continue from existing prose

    AI analyzes the existing text's style and continues seamlessly.
    Maintains:
    - Tense and POV
    - Sentence structure and rhythm
    - Voice and tone
    - Character consistency
    """
    service = get_draft_service(request.preset, db)

    try:
        result = await service.continue_from_text(
            project_id=project_id,
            existing_text=request.existing_text,
            continuation_prompt=request.continuation_prompt,
            target_word_count=request.target_word_count
        )

        return GenerationResponse(
            text=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            cost=result.cost,
            quality_score=result.quality_score,
            refinement_iterations=result.refinement_iterations,
            metadata=result.metadata,
            timestamp=result.timestamp.isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Continuation failed: {str(e)}"
        )


@router.post("/projects/{project_id}/ai/refine", response_model=GenerationResponse)
async def refine_prose(
    project_id: int,
    request: RefinementRequest,
    user: User = Depends(require_project_access(min_role=CollaboratorRole.WRITER)),
    db: Session = Depends(get_db)
):
    """
    Refine existing prose based on specific goals

    Example refinement goals:
    - "Add more sensory details"
    - "Tighten pacing, remove unnecessary words"
    - "Strengthen character voice"
    - "Show more, tell less"
    - "Increase tension"
    """
    service = get_draft_service(request.preset, db)

    try:
        result = await service.refine_prose(
            project_id=project_id,
            prose=request.prose,
            refinement_goals=request.refinement_goals,
            preserve_length=request.preserve_length
        )

        return GenerationResponse(
            text=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            cost=result.cost,
            quality_score=result.quality_score,
            refinement_iterations=result.refinement_iterations,
            metadata=result.metadata,
            timestamp=result.timestamp.isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Refinement failed: {str(e)}"
        )


@router.get("/ai/presets")
async def list_presets():
    """
    List available generation presets

    Returns information about each preset configuration
    """
    return {
        "presets": [
            {
                "id": "fast_draft",
                "name": "Fast Draft",
                "description": "Quick generation for brainstorming",
                "model": "gpt-4o-mini",
                "temperature": 0.9,
                "refinement_iterations": 1,
                "speed": "very_fast",
                "cost": "very_low",
                "best_for": ["Rapid prototyping", "Quick ideas", "Rough drafts"]
            },
            {
                "id": "balanced",
                "name": "Balanced",
                "description": "Good quality with reasonable speed",
                "model": "claude-sonnet-3.5",
                "temperature": 0.8,
                "refinement_iterations": 2,
                "speed": "medium",
                "cost": "medium",
                "best_for": ["General writing", "Most use cases", "Good value"]
            },
            {
                "id": "premium",
                "name": "Premium",
                "description": "Highest quality, slower generation",
                "model": "claude-opus-4",
                "temperature": 0.7,
                "refinement_iterations": 3,
                "speed": "slow",
                "cost": "high",
                "best_for": ["Final drafts", "Complex scenes", "Publishable quality"]
            },
            {
                "id": "creative_burst",
                "name": "Creative Burst",
                "description": "High creativity for experimental ideas",
                "model": "gpt-4o",
                "temperature": 1.2,
                "refinement_iterations": 2,
                "speed": "medium",
                "cost": "medium",
                "best_for": ["Brainstorming", "Unexpected twists", "Creative exploration"]
            },
            {
                "id": "canon_strict",
                "name": "Canon Strict",
                "description": "Maximum canon consistency",
                "model": "claude-opus-4",
                "temperature": 0.6,
                "refinement_iterations": 3,
                "speed": "slow",
                "cost": "high",
                "best_for": ["Series consistency", "Complex worldbuilding", "Continuity-critical"]
            }
        ]
    }


@router.get("/projects/{project_id}/ai/usage-estimate")
async def estimate_usage(
    project_id: int,
    scene_count: int,
    words_per_scene: int,
    preset: str = "balanced",
    user: User = Depends(require_project_access(min_role=CollaboratorRole.VIEWER))
):
    """
    Estimate cost and time for generating scenes

    Helps users plan their AI usage within subscription limits
    """
    # Rough estimates based on preset
    estimates = {
        "fast_draft": {"tokens_per_word": 1.5, "cost_per_1k": 0.0003, "seconds_per_scene": 15},
        "balanced": {"tokens_per_word": 2.0, "cost_per_1k": 0.006, "seconds_per_scene": 30},
        "premium": {"tokens_per_word": 3.0, "cost_per_1k": 0.03, "seconds_per_scene": 60},
        "creative_burst": {"tokens_per_word": 2.5, "cost_per_1k": 0.008, "seconds_per_scene": 35},
        "canon_strict": {"tokens_per_word": 3.5, "cost_per_1k": 0.035, "seconds_per_scene": 70}
    }

    config = estimates.get(preset, estimates["balanced"])

    total_words = scene_count * words_per_scene
    total_tokens = int(total_words * config["tokens_per_word"])
    total_cost = (total_tokens / 1000) * config["cost_per_1k"]
    total_time_seconds = scene_count * config["seconds_per_scene"]

    return {
        "preset": preset,
        "scene_count": scene_count,
        "words_per_scene": words_per_scene,
        "total_words": total_words,
        "estimated_tokens": total_tokens,
        "estimated_cost_usd": round(total_cost, 2),
        "estimated_time_minutes": round(total_time_seconds / 60, 1),
        "llm_calls_used": scene_count * 3,  # Approximate (plan + write + critique)
    }
