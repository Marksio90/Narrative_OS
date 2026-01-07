"""
Pydantic schemas for QC API
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ValidateChapterRequest(BaseModel):
    """Request to validate chapter"""
    project_id: int
    chapter_content: str = Field(..., min_length=1)
    chapter_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chapter info: number, goal, POV character, etc."
    )
    canon_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Relevant canon: characters, locations, rules"
    )


class QCIssueResponse(BaseModel):
    """QC issue"""
    category: str  # continuity, character, plot, contract, style
    severity: str  # blocker, warning, suggestion
    description: str
    location: Optional[str]
    suggested_fix: Optional[str]


class DetectedPromiseResponse(BaseModel):
    """Detected promise"""
    setup_description: str
    payoff_required: str
    confidence: float
    chapter: int
    scene: Optional[int]
    suggested_deadline: Optional[int]


class QCReportResponse(BaseModel):
    """Complete QC validation report"""
    passed: bool
    score: int = Field(..., ge=0, le=100, description="Quality score")
    issues: List[QCIssueResponse]
    issue_count: int
    blockers: int
    warnings: int
    suggestions: int
    detected_promises: List[DetectedPromiseResponse]
    breakdown: Dict[str, int] = Field(description="Issues by category")
