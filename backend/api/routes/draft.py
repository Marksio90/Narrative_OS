"""
Draft API Routes

Scene-by-scene prose generation with quality gates
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database.base import get_db
from services.draft.service import DraftService
from api.schemas.draft import (
    GenerateSceneRequest,
    GenerateChapterRequest,
    SceneDraftResponse,
    ChapterDraftResponse,
)

router = APIRouter()


def get_draft_service(db: Session = Depends(get_db)) -> DraftService:
    """Dependency to get Draft service"""
    return DraftService(db)


@router.post("/generate-scene", response_model=SceneDraftResponse)
async def generate_scene(
    data: GenerateSceneRequest,
    service: DraftService = Depends(get_draft_service),
):
    """
    Generate prose for a single scene

    **Pipeline:**
    1. **Input:** Scene card + Canon context
    2. **Generate:** Prose from scene requirements
       - Uses scene goal, conflict, what_changes
       - Respects participants, location, timing
       - Follows style profile (tone, pacing, focus)
    3. **Extract:** New canon facts from prose
       - Physical details (scars, items, etc.)
       - Character revelations
       - Relationship changes
    4. **Detect:** New narrative promises
       - Auto-detect Chekhov's Guns
       - Track for future payoff
    5. **Validate:** QC + Contracts (if auto_validate=true)
       - Continuity check
       - Character consistency
       - Plot logic
       - Contract compliance
    6. **Output:** Validated prose with report

    **Status Values:**
    - `passed` - QC passed, ready to accept
    - `needs_regeneration` - QC failed or low score
    - `validating` - Validation in progress
    - `failed` - Generation error

    **Use Case:**
    ```
    1. Create scene card with goal, conflict, what_changes
    2. POST /api/draft/generate-scene
    3. Review QC report and extracted facts
    4. If passed: Accept and update scene
    5. If failed: Fix issues or regenerate
    ```

    **Returns:**
    - Prose text
    - Word count
    - QC validation report
    - Extracted canon facts
    - Detected promises
    - Suggestions for improvement
    """
    try:
        result = await service.generate_scene(
            scene_id=data.scene_id,
            canon_context=data.canon_context,
            style_profile=data.style_profile,
            auto_validate=data.auto_validate,
        )

        return SceneDraftResponse(
            status=result.status,
            prose=result.prose,
            word_count=result.word_count,
            qc_report=result.qc_report,
            extracted_facts=result.extracted_facts,
            detected_promises=result.detected_promises,
            suggestions=result.suggestions,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scene generation error: {str(e)}"
        )


@router.post("/generate-chapter", response_model=ChapterDraftResponse)
async def generate_chapter(
    data: GenerateChapterRequest,
    service: DraftService = Depends(get_draft_service),
):
    """
    Generate prose for entire chapter (scene by scene)

    **Pipeline:**
    1. Get chapter and all scene cards (in order)
    2. For each scene:
       - Generate prose
       - Extract facts
       - Detect promises
    3. Combine all scenes into full chapter
    4. Validate complete chapter with QC
    5. Update chapter content in DB
    6. Return comprehensive result

    **Benefits of Scene-by-Scene:**
    - More control over structure
    - Better fact extraction per scene
    - Promise detection at scene level
    - Can regenerate individual scenes if needed

    **Auto-Updates:**
    - Chapter content saved to DB
    - Word count updated
    - Status set to 'drafted' (if passed) or 'planned' (if failed)

    **Returns:**
    - Full chapter prose
    - Individual scene results
    - Combined QC report
    - All extracted facts
    - All detected promises
    - Overall status

    **Use Case:**
    ```
    1. Plan chapter with scene cards
    2. POST /api/draft/generate-chapter
    3. Review chapter-level QC report
    4. Check each scene's quality
    5. Accept or revise specific scenes
    ```
    """
    try:
        result = await service.generate_chapter(
            chapter_id=data.chapter_id,
            canon_context=data.canon_context,
            style_profile=data.style_profile,
        )

        return ChapterDraftResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chapter generation error: {str(e)}"
        )
