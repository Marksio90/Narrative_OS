"""
Promise Ledger API Routes

Endpoints for automatic promise detection and tracking
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from core.database.base import get_db
from services.canon.promise_ledger import PromiseLedgerService
from api.schemas.promise_ledger import (
    DetectPromisesRequest,
    DetectedPromiseResponse,
    ValidatePayoffRequest,
    PayoffValidationResponse,
    LedgerReportResponse,
)
from api.schemas.canon import PromiseResponse

router = APIRouter()


def get_ledger_service(db: Session = Depends(get_db)) -> PromiseLedgerService:
    """Dependency to get Promise Ledger service"""
    return PromiseLedgerService(db)


@router.post("/detect", response_model=List[DetectedPromiseResponse])
async def detect_promises(
    data: DetectPromisesRequest,
    service: PromiseLedgerService = Depends(get_ledger_service),
):
    """
    Automatically detect narrative promises in text

    **What it detects:**
    - Chekhov's Guns (items/details that must pay off later)
    - Character goals and vows
    - Mysteries and unanswered questions
    - Foreshadowing and prophecies
    - Threats and warnings

    **Returns:**
    - List of detected promises
    - Required payoffs
    - Confidence scores
    - Suggested deadlines
    """
    try:
        promises = await service.detect_promises(
            text=data.text,
            chapter=data.chapter,
            scene=data.scene,
            context=data.context,
        )
        return [p.to_dict() for p in promises]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@router.get("/open", response_model=List[PromiseResponse])
async def get_open_promises(
    project_id: int = Query(..., description="Project ID"),
    before_chapter: Optional[int] = Query(None, description="Only before this chapter"),
    service: PromiseLedgerService = Depends(get_ledger_service),
):
    """
    Get all open (unfulfilled) promises

    Useful for checking what promises still need payoff
    """
    promises = service.get_open_promises(project_id, before_chapter)
    return promises


@router.get("/near-deadline", response_model=List[PromiseResponse])
async def get_promises_near_deadline(
    project_id: int = Query(...),
    current_chapter: int = Query(..., ge=1),
    lookahead: int = Query(3, ge=1, le=10, description="Chapters ahead to check"),
    service: PromiseLedgerService = Depends(get_ledger_service),
):
    """
    Get promises approaching their deadline

    **Use case:**
    Before writing chapter N, check what promises need to be resolved soon
    """
    promises = service.get_promises_near_deadline(
        project_id=project_id,
        current_chapter=current_chapter,
        lookahead=lookahead,
    )
    return promises


@router.get("/overdue", response_model=List[PromiseResponse])
async def get_overdue_promises(
    project_id: int = Query(...),
    current_chapter: int = Query(..., ge=1),
    service: PromiseLedgerService = Depends(get_ledger_service),
):
    """
    Get promises past their deadline

    **These are problems** - promises that should have been fulfilled but weren't
    """
    promises = service.get_overdue_promises(project_id, current_chapter)
    return promises


@router.post("/{promise_id}/validate-payoff", response_model=PayoffValidationResponse)
async def validate_payoff(
    promise_id: int,
    data: ValidatePayoffRequest,
    service: PromiseLedgerService = Depends(get_ledger_service),
):
    """
    Validate that proposed payoff fulfills the promise

    **Use case:**
    After writing a scene that might fulfill a promise, validate it
    """
    try:
        result = await service.validate_payoff(
            promise_id=promise_id,
            payoff_text=data.payoff_text,
            payoff_chapter=data.payoff_chapter,
            payoff_scene=data.payoff_scene,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.get("/report", response_model=LedgerReportResponse)
async def get_ledger_report(
    project_id: int = Query(...),
    current_chapter: int = Query(..., ge=1),
    service: PromiseLedgerService = Depends(get_ledger_service),
):
    """
    Get comprehensive promise ledger report

    **Health metrics:**
    - Total promises
    - Open/fulfilled/abandoned counts
    - Promises near deadline
    - Overdue promises
    - Health score (0-100)
    - Warnings

    **Use case:**
    Dashboard showing promise health before starting new chapter
    """
    report = service.get_ledger_report(project_id, current_chapter)
    return report
