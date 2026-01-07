"""
Pydantic schemas for Canon Contracts API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContractCreate(BaseModel):
    """Create canon contract"""
    project_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    constraint: str = Field(..., min_length=1, description="The actual rule in natural language")
    rule_type: str = Field(..., description="world, character, magic, plot, style")
    severity: str = Field(default="must", description="must, should, prefer")
    applies_to: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, str]]] = None


class ContractUpdate(BaseModel):
    """Update canon contract"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    constraint: Optional[str] = None
    rule_type: Optional[str] = None
    severity: Optional[str] = None
    applies_to: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, str]]] = None
    active: Optional[bool] = None


class ContractResponse(BaseModel):
    """Canon contract response"""
    id: int
    project_id: int
    name: str
    description: str
    constraint: str
    rule_type: str
    severity: str
    applies_to: Dict[str, Any]
    examples: List[Dict[str, str]]
    active: bool
    violation_count: int
    validation_prompt: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ValidateTextRequest(BaseModel):
    """Request to validate text against contracts"""
    text: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    rule_types: Optional[List[str]] = None


class ContractViolationResponse(BaseModel):
    """Contract violation"""
    contract_id: int
    contract_name: str
    violation_description: str
    severity: str
    suggested_fix: Optional[str] = None


class ValidationResultResponse(BaseModel):
    """Text validation result"""
    valid: bool
    violation_count: int
    violations: List[ContractViolationResponse]
    severity_breakdown: Dict[str, int]


class ValidateChapterRequest(BaseModel):
    """Request to validate chapter"""
    chapter_content: str = Field(..., min_length=1)
    chapter_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chapter info: number, POV character, etc."
    )
