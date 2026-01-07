"""
Pydantic schemas for Draft API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GenerateSceneRequest(BaseModel):
    """Request to generate scene prose"""
    scene_id: int
    canon_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Relevant canon: characters, locations, rules"
    )
    style_profile: Optional[Dict[str, Any]] = None
    auto_validate: bool = Field(
        default=True,
        description="Run QC validation automatically"
    )


class GenerateChapterRequest(BaseModel):
    """Request to generate entire chapter"""
    chapter_id: int
    canon_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Relevant canon context"
    )
    style_profile: Optional[Dict[str, Any]] = None


class ExtractedFactsResponse(BaseModel):
    """Extracted canon facts"""
    character: List[Dict[str, str]] = Field(default_factory=list)
    location: List[Dict[str, str]] = Field(default_factory=list)
    item: List[Dict[str, str]] = Field(default_factory=list)
    relationship: List[Dict[str, str]] = Field(default_factory=list)


class SceneDraftResponse(BaseModel):
    """Scene generation result"""
    status: str  # generating, validating, passed, failed, needs_regeneration
    prose: str
    word_count: int
    qc_report: Optional[Dict[str, Any]] = None
    extracted_facts: Optional[ExtractedFactsResponse] = None
    detected_promises: Optional[List[Dict[str, Any]]] = None
    suggestions: List[str] = Field(default_factory=list)


class SceneResultResponse(BaseModel):
    """Individual scene result within chapter"""
    scene_number: int
    result: SceneDraftResponse


class ChapterDraftResponse(BaseModel):
    """Chapter generation result"""
    chapter_id: int
    chapter_number: int
    prose: str
    word_count: int
    scene_count: int
    scene_results: List[SceneResultResponse]
    qc_report: Dict[str, Any]
    extracted_facts: ExtractedFactsResponse
    detected_promises: List[Dict[str, Any]]
    status: str  # passed, needs_revision
