"""
Export Service
Coordinates manuscript assembly and export to various formats
"""
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

from core.models.base import Project
from .docx_generator import generate_manuscript_docx
from .epub_generator import generate_manuscript_epub
from .pdf_generator import generate_manuscript_pdf


ExportFormat = Literal['docx', 'epub', 'pdf']


class ExportService:
    """
    Service for assembling and exporting manuscripts

    Coordinates:
    - Fetching project data from database
    - Assembling chapters in order
    - Generating exports in requested format
    """

    def __init__(self, db: Session):
        self.db = db

    async def export_project(
        self,
        project_id: int,
        format: ExportFormat,
        include_prologue: bool = True,
        include_epilogue: bool = True,
        include_toc: bool = True,
        custom_title: Optional[str] = None,
        custom_author: Optional[str] = None
    ) -> bytes:
        """
        Export a complete project in specified format

        Args:
            project_id: Project ID to export
            format: Output format ('docx', 'epub', 'pdf')
            include_prologue: Include prologue if present
            include_epilogue: Include epilogue if present
            include_toc: Include table of contents (DOCX only)
            custom_title: Override project title
            custom_author: Override author name

        Returns:
            File content as bytes

        Raises:
            ValueError: If project not found or invalid format
        """
        # Fetch project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Assemble manuscript data
        manuscript = await self._assemble_manuscript(
            project=project,
            include_prologue=include_prologue,
            include_epilogue=include_epilogue
        )

        # Override title/author if provided
        if custom_title:
            manuscript['title'] = custom_title
        if custom_author:
            manuscript['author'] = custom_author

        # Generate export based on format
        if format == 'docx':
            return generate_manuscript_docx(
                project_title=manuscript['title'],
                author_name=manuscript['author'],
                chapters=manuscript['chapters'],
                genre=manuscript.get('genre'),
                prologue=manuscript.get('prologue'),
                epilogue=manuscript.get('epilogue'),
                include_toc=include_toc
            )
        elif format == 'epub':
            return generate_manuscript_epub(
                project_title=manuscript['title'],
                author_name=manuscript['author'],
                chapters=manuscript['chapters'],
                genre=manuscript.get('genre'),
                prologue=manuscript.get('prologue'),
                epilogue=manuscript.get('epilogue'),
                description=manuscript.get('description')
            )
        elif format == 'pdf':
            return generate_manuscript_pdf(
                project_title=manuscript['title'],
                author_name=manuscript['author'],
                chapters=manuscript['chapters'],
                genre=manuscript.get('genre'),
                prologue=manuscript.get('prologue'),
                epilogue=manuscript.get('epilogue')
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _get_project(self, project_id: int) -> Optional[Project]:
        """Fetch project from database"""
        # For sync session
        if hasattr(self.db, 'execute'):
            result = self.db.execute(
                select(Project).where(Project.id == project_id)
            )
            return result.scalar_one_or_none()
        else:
            # For async session
            result = await self.db.execute(
                select(Project).where(Project.id == project_id)
            )
            return result.scalar_one_or_none()

    async def _assemble_manuscript(
        self,
        project: Project,
        include_prologue: bool = True,
        include_epilogue: bool = True
    ) -> Dict[str, Any]:
        """
        Assemble manuscript from project data

        Returns:
            Dict with title, author, chapters, prologue, epilogue
        """
        # TODO: Fetch actual scenes/prose from database when Draft service is integrated
        # For now, return mock structure

        manuscript = {
            'title': project.title,
            'author': 'Author Name',  # TODO: Get from project owner
            'genre': project.genre,
            'description': None,
            'chapters': [],
            'prologue': None,
            'epilogue': None
        }

        # Mock chapters for testing
        # In production, this will fetch from scenes table
        mock_chapters = [
            {
                'number': 1,
                'title': 'The Beginning',
                'content': '''The sun rose over the horizon, painting the sky in shades of amber and gold. Sarah stood at the edge of the cliff, her heart pounding with anticipation.

She had waited for this moment her entire life. The ancient map clutched in her hand promised answers to questions she'd long forgotten how to ask.

###

Hours later, deep in the forest, she discovered the first clue. A weathered stone marker, covered in moss and mystery.'''
            },
            {
                'number': 2,
                'title': 'The Discovery',
                'content': '''The cave entrance was hidden behind a waterfall, just as the map had indicated. Sarah's torch flickered as she ventured into the darkness.

Ancient symbols covered the walls, their meaning lost to time. But one image stood out—a constellation she recognized from her grandmother's stories.

This was no ordinary cave. This was the Archive.'''
            }
        ]

        manuscript['chapters'] = mock_chapters

        # Mock prologue/epilogue
        if include_prologue:
            manuscript['prologue'] = '''Before the beginning, there was only silence. And in that silence, a story waited to be told.

This is that story.'''

        if include_epilogue:
            manuscript['epilogue'] = '''The journey had only just begun. But Sarah knew, with absolute certainty, that she was finally on the right path.

The Archive had revealed its first secret. Many more awaited.'''

        return manuscript

    def get_filename(
        self,
        project_title: str,
        format: ExportFormat,
        timestamp: bool = True
    ) -> str:
        """
        Generate appropriate filename for export

        Args:
            project_title: Project title
            format: Export format
            timestamp: Whether to append timestamp

        Returns:
            Sanitized filename with extension
        """
        # Sanitize title for filename
        safe_title = "".join(
            c for c in project_title
            if c.isalnum() or c in (' ', '-', '_')
        ).strip()
        safe_title = safe_title.replace(' ', '_')

        # Add timestamp if requested
        if timestamp:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_title}_{ts}.{format}"
        else:
            filename = f"{safe_title}.{format}"

        return filename
