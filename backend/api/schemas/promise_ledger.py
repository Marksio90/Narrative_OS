"""
Pydantic schemas for Promise Ledger API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DetectPromisesRequest(BaseModel):
    """Request to detect promises in text"""
    text: str = Field(..., min_length=1)
    chapter: int = Field(..., ge=1)
    scene: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class DetectedPromiseResponse(BaseModel):
    """Detected promise"""
    setup_description: str
    payoff_required: str
    confidence: float
    chapter: int
    scene: Optional[int]
    suggested_deadline: Optional[int]


class ValidatePayoffRequest(BaseModel):
    """Request to validate payoff"""
    payoff_text: str = Field(..., min_length=1)
    payoff_chapter: int = Field(..., ge=1)
    payoff_scene: Optional[int] = None


class PayoffValidationResponse(BaseModel):
    """Payoff validation result"""
    valid: bool
    reason: str
    completeness: int = Field(..., ge=0, le=100)
    suggestions: Optional[str] = None
    error: Optional[str] = None


class LedgerReportResponse(BaseModel):
    """Promise ledger health report"""
    total_promises: int
    open_count: int
    fulfilled_count: int
    abandoned_count: int
    near_deadline_count: int
    overdue_count: int
    health_score: int = Field(..., ge=0, le=100)
    warnings: List[str]
