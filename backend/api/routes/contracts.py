"""
Canon Contracts API Routes

Endpoints for managing and validating hard consistency rules
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database.base import get_db
from services.canon.contracts import CanonContractsService
from api.schemas.contracts import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ValidateTextRequest,
    ValidationResultResponse,
    ValidateChapterRequest,
)
from api.schemas.canon import MessageResponse

router = APIRouter()


def get_contracts_service(db: Session = Depends(get_db)) -> CanonContractsService:
    """Dependency to get Contracts service"""
    return CanonContractsService(db)


@router.post("/", response_model=ContractResponse, status_code=201)
async def create_contract(
    data: ContractCreate,
    service: CanonContractsService = Depends(get_contracts_service),
):
    """
    Create a new canon contract

    Canon contracts are hard rules that AI generation must respect.

    **Examples:**
    - "Magic always requires a blood sacrifice"
    - "The protagonist never kills without remorse"
    - "Time travel is impossible in this world"
    - "All dialogue must be in present tense"

    **Severity levels:**
    - `must`: Absolute rule, violations block generation
    - `should`: Strong preference, violations trigger warnings
    - `prefer`: Soft preference, violations logged
    """
    try:
        contract = service.create_contract(
            project_id=data.project_id,
            name=data.name,
            description=data.description,
            constraint=data.constraint,
            rule_type=data.rule_type,
            severity=data.severity,
            applies_to=data.applies_to,
            examples=data.examples,
        )
        return contract
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    service: CanonContractsService = Depends(get_contracts_service),
):
    """Get canon contract by ID"""
    contract = service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/", response_model=List[ContractResponse])
async def list_contracts(
    project_id: int = Query(..., description="Project ID"),
    active_only: bool = Query(True, description="Only return active contracts"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    service: CanonContractsService = Depends(get_contracts_service),
):
    """
    List canon contracts for a project

    Filter by rule type: world, character, magic, plot, style
    """
    contracts = service.list_contracts(
        project_id=project_id,
        active_only=active_only,
        rule_type=rule_type,
    )
    return contracts


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    data: ContractUpdate,
    service: CanonContractsService = Depends(get_contracts_service),
):
    """
    Update canon contract

    Can update rule, severity, examples, or deactivate
    """
    try:
        contract = service.update_contract(
            contract_id=contract_id,
            **data.model_dump(exclude_unset=True),
        )
        return contract
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{contract_id}", response_model=MessageResponse)
async def delete_contract(
    contract_id: int,
    service: CanonContractsService = Depends(get_contracts_service),
):
    """
    Delete (deactivate) canon contract

    Contracts are soft-deleted (marked inactive) to preserve history
    """
    success = service.delete_contract(contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return MessageResponse(message="Contract deactivated successfully")


@router.post("/validate", response_model=ValidationResultResponse)
async def validate_text(
    project_id: int = Query(..., description="Project ID"),
    data: ValidateTextRequest = ...,
    service: CanonContractsService = Depends(get_contracts_service),
):
    """
    Validate text against all active canon contracts

    **Use cases:**
    - Validate generated scene before accepting
    - Check manually written prose
    - Pre-validate chapter before generation

    **Returns:**
    - List of violations (empty if all contracts satisfied)
    - Severity breakdown (must/should/prefer)
    - Suggested fixes for violations
    """
    try:
        violations = await service.validate_text(
            project_id=project_id,
            text=data.text,
            context=data.context,
            rule_types=data.rule_types,
        )

        return ValidationResultResponse(
            valid=len(violations) == 0,
            violation_count=len(violations),
            violations=[
                {
                    "contract_id": v.contract_id,
                    "contract_name": v.contract_name,
                    "violation_description": v.violation_description,
                    "severity": v.severity,
                    "suggested_fix": v.suggested_fix,
                }
                for v in violations
            ],
            severity_breakdown=service._count_by_severity(violations),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post("/validate-chapter", response_model=ValidationResultResponse)
async def validate_chapter(
    project_id: int = Query(..., description="Project ID"),
    data: ValidateChapterRequest = ...,
    service: CanonContractsService = Depends(get_contracts_service),
):
    """
    Validate entire chapter against canon contracts

    Specialized endpoint for chapter validation with metadata context
    """
    try:
        result = await service.validate_chapter(
            project_id=project_id,
            chapter_content=data.chapter_content,
            chapter_metadata=data.chapter_metadata,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chapter validation error: {str(e)}")
