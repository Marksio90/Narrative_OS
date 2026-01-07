"""
Quality Control API Routes

Writers' room validation system
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database.base import get_db
from services.qc.service import QCService
from api.schemas.qc import (
    ValidateChapterRequest,
    QCReportResponse,
)

router = APIRouter()


def get_qc_service(db: Session = Depends(get_db)) -> QCService:
    """Dependency to get QC service"""
    return QCService(db)


@router.post("/validate-chapter", response_model=QCReportResponse)
async def validate_chapter(
    data: ValidateChapterRequest,
    service: QCService = Depends(get_qc_service),
):
    """
    Validate chapter with multi-agent writers' room system

    **Validation Agents:**
    - **Continuity Editor**: Timeline, locations, items, physics
    - **Character Editor**: Behavior, voice, motivation, limits
    - **Plot Editor**: Logic, cause/effect, deus ex machina, stakes
    - **Contract Validator**: Hard canon rules compliance
    - **Promise Detector**: Auto-detect new narrative promises

    **Quality Scoring:**
    - 100 = Perfect, no issues
    - Penalties: blocker (-30), warning (-10), suggestion (-3)
    - Minimum 0

    **Pass Criteria:**
    - No blockers = PASS
    - Any blockers = FAIL (must fix before accepting)

    **Use Case:**
    Before accepting generated or manually written chapter:
    1. Submit for QC validation
    2. Review issues by severity and category
    3. Fix all blockers
    4. Optional: fix warnings and suggestions
    5. Accept chapter or regenerate

    **Returns:**
    - Comprehensive QC report with issues, score, detected promises
    """
    try:
        report = await service.validate_chapter(
            project_id=data.project_id,
            chapter_content=data.chapter_content,
            chapter_metadata=data.chapter_metadata,
            canon_context=data.canon_context,
        )

        # Convert to response format
        return QCReportResponse(
            passed=report["passed"],
            score=report["score"],
            issues=[
                {
                    "category": issue["category"],
                    "severity": issue["severity"],
                    "description": issue["description"],
                    "location": issue.get("location"),
                    "suggested_fix": issue.get("suggested_fix"),
                }
                for issue in report["issues"]
            ],
            issue_count=report["issue_count"],
            blockers=report["blockers"],
            warnings=report["warnings"],
            suggestions=report["suggestions"],
            detected_promises=[
                {
                    "setup_description": p["setup_description"],
                    "payoff_required": p["payoff_required"],
                    "confidence": p["confidence"],
                    "chapter": p["chapter"],
                    "scene": p.get("scene"),
                    "suggested_deadline": p.get("suggested_deadline"),
                }
                for p in report["detected_promises"]
            ],
            breakdown=report["breakdown"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"QC validation error: {str(e)}"
        )
