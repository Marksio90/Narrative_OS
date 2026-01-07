"""
Export API Routes
REST endpoints for manuscript export
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Literal
import io

from core.database.base import get_db
from core.auth.config import current_active_user
from core.auth.permissions import require_project_access
from core.models.user import User, CollaboratorRole
from services.export.service import ExportService
from api.schemas.export import ExportRequest, ExportResponse

router = APIRouter()


def get_export_service(db: Session = Depends(get_db)) -> ExportService:
    """Dependency to get Export service"""
    return ExportService(db)


@router.post("/projects/{project_id}/export", response_class=StreamingResponse)
async def export_project(
    project_id: int,
    format: Literal['docx', 'epub', 'pdf'] = Query(..., description="Export format"),
    include_prologue: bool = Query(True, description="Include prologue if present"),
    include_epilogue: bool = Query(True, description="Include epilogue if present"),
    include_toc: bool = Query(True, description="Include table of contents (DOCX only)"),
    user: User = Depends(require_project_access(min_role=CollaboratorRole.VIEWER)),
    service: ExportService = Depends(get_export_service),
):
    """
    Export project to DOCX, EPUB, or PDF

    Requires at least VIEWER access to the project.

    **Formats:**
    - `docx`: Microsoft Word format (editable)
    - `epub`: E-book format (for e-readers)
    - `pdf`: Portable Document Format (print-ready)

    **Features:**
    - Professional manuscript formatting
    - Cover page with metadata
    - Chapter organization
    - Page numbers (DOCX, PDF)
    - Scene breaks
    """
    try:
        # Generate export
        file_bytes = await service.export_project(
            project_id=project_id,
            format=format,
            include_prologue=include_prologue,
            include_epilogue=include_epilogue,
            include_toc=include_toc
        )

        # Get project for filename
        from core.models.base import Project
        project = service.db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Generate filename
        filename = service.get_filename(
            project_title=project.title,
            format=format,
            timestamp=True
        )

        # Content type mapping
        content_types = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'epub': 'application/epub+zip',
            'pdf': 'application/pdf'
        }

        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=content_types[format],
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/projects/{project_id}/export/preview")
async def get_export_preview(
    project_id: int,
    user: User = Depends(require_project_access(min_role=CollaboratorRole.VIEWER)),
    service: ExportService = Depends(get_export_service),
):
    """
    Get export preview information

    Returns metadata about what will be exported:
    - Chapter count
    - Word count
    - Estimated page count
    - Available formats
    """
    from core.models.base import Project

    project = service.db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # TODO: Calculate real stats from database when Draft service is integrated
    # For now, return mock data

    return {
        "project_id": project_id,
        "title": project.title,
        "genre": project.genre,
        "chapter_count": 2,  # Mock
        "word_count": 750,  # Mock
        "estimated_pages": 3,  # Mock (250 words per page)
        "available_formats": ["docx", "epub", "pdf"],
        "has_prologue": True,
        "has_epilogue": True,
    }


@router.get("/export/formats")
async def list_export_formats():
    """
    List all available export formats with descriptions

    Returns information about supported export formats
    """
    return {
        "formats": [
            {
                "id": "docx",
                "name": "Microsoft Word",
                "extension": ".docx",
                "description": "Editable Word document with professional manuscript formatting",
                "features": [
                    "Cover page",
                    "Table of contents",
                    "Page numbers",
                    "Chapter organization",
                    "Scene breaks",
                    "Standard manuscript format (1\" margins, Times 12pt, double-spaced)"
                ],
                "use_cases": [
                    "Editing and revisions",
                    "Submission to publishers",
                    "Sharing with editors"
                ]
            },
            {
                "id": "epub",
                "name": "EPUB",
                "extension": ".epub",
                "description": "E-book format compatible with most e-readers",
                "features": [
                    "Responsive layout",
                    "Navigation menu",
                    "Adjustable font size",
                    "Dark mode support",
                    "Cover image support",
                    "Metadata (author, genre, ISBN)"
                ],
                "use_cases": [
                    "E-readers (Kindle, Kobo, etc.)",
                    "Self-publishing",
                    "Distribution"
                ]
            },
            {
                "id": "pdf",
                "name": "PDF",
                "extension": ".pdf",
                "description": "Universal document format, print-ready",
                "features": [
                    "Fixed layout",
                    "Page numbers",
                    "Professional typography",
                    "Print-ready formatting",
                    "Universal compatibility"
                ],
                "use_cases": [
                    "Printing",
                    "Archiving",
                    "Sharing for review",
                    "Print-on-demand publishing"
                ]
            }
        ]
    }
