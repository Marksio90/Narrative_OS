"""
Pydantic schemas for export functionality
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class ExportRequest(BaseModel):
    """Request to export a project"""
    format: Literal['docx', 'epub', 'pdf'] = Field(..., description="Export format")
    include_prologue: bool = Field(True, description="Include prologue if present")
    include_epilogue: bool = Field(True, description="Include epilogue if present")
    include_toc: bool = Field(True, description="Include table of contents (DOCX only)")
    custom_title: Optional[str] = Field(None, description="Override project title")
    custom_author: Optional[str] = Field(None, description="Override author name")


class ExportResponse(BaseModel):
    """Response after export generation"""
    filename: str
    format: str
    size_bytes: int
    download_url: str


class ExportPreview(BaseModel):
    """Preview information about an export"""
    project_id: int
    title: str
    genre: Optional[str]
    chapter_count: int
    word_count: int
    estimated_pages: int
    available_formats: List[str]
    has_prologue: bool
    has_epilogue: bool


class ExportFormat(BaseModel):
    """Information about an export format"""
    id: str
    name: str
    extension: str
    description: str
    features: List[str]
    use_cases: List[str]
