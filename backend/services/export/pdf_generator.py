"""
PDF Export Generator
Professional manuscript formatting for PDF
Uses ReportLab for modern PDF generation with typography control
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Frame,
    PageTemplate,
    NextPageTemplate
)
from reportlab.pdfgen import canvas
from typing import Optional, List, Dict, Any
from datetime import datetime
import io


class NumberedCanvas(canvas.Canvas):
    """Canvas with page numbers"""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to all pages"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Draw page number at bottom center"""
        self.setFont("Times-Roman", 10)
        self.drawCentredString(
            letter[0] / 2.0,
            0.5 * inch,
            f"Page {self._pageNumber} of {page_count}"
        )


class PdfGenerator:
    """
    Generate professional PDF manuscripts

    Features:
    - Standard manuscript format (1" margins, Times 12pt)
    - Cover page with metadata
    - Page numbers
    - Chapter headings with page breaks
    - Scene separators
    - Professional typography
    """

    def __init__(self):
        self.buffer = io.BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch * 1.2,  # Extra space for page numbers
        )

        self.story = []
        self.styles = self._create_styles()

    def _create_styles(self):
        """Create professional paragraph styles"""
        styles = getSampleStyleSheet()

        # Cover title style
        styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=styles['Heading1'],
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Times-Bold'
        ))

        # Cover subtitle
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Times-Italic'
        ))

        # Cover author
        styles.add(ParagraphStyle(
            name='CoverAuthor',
            parent=styles['Normal'],
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Times-Roman'
        ))

        # Chapter heading
        styles.add(ParagraphStyle(
            name='ChapterHeading',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=24,
            spaceBefore=0,
            fontName='Times-Bold',
            keepWithNext=True
        ))

        # Body text (standard manuscript format)
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=12,
            leading=24,  # Double-spaced
            alignment=TA_JUSTIFY,
            firstLineIndent=0.5 * inch,
            fontName='Times-Roman',
            spaceAfter=0
        ))

        # First paragraph (no indent)
        styles.add(ParagraphStyle(
            name='FirstParagraph',
            parent=styles['BodyText'],
            firstLineIndent=0
        ))

        # Scene break
        styles.add(ParagraphStyle(
            name='SceneBreak',
            parent=styles['Normal'],
            fontSize=12,
            leading=24,
            alignment=TA_CENTER,
            fontName='Times-Roman',
            spaceAfter=12,
            spaceBefore=12
        ))

        # Metadata
        styles.add(ParagraphStyle(
            name='Metadata',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            fontName='Times-Roman',
            textColor='#666666'
        ))

        return styles

    def add_cover_page(
        self,
        title: str,
        author: str,
        genre: Optional[str] = None,
        word_count: Optional[int] = None,
        subtitle: Optional[str] = None
    ):
        """Add professional cover page"""
        # Vertical spacing (approx 1/3 page)
        self.story.append(Spacer(1, 3 * inch))

        # Title
        self.story.append(Paragraph(title, self.styles['CoverTitle']))

        # Subtitle
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['CoverSubtitle']))
            self.story.append(Spacer(1, 0.2 * inch))

        # Spacing
        self.story.append(Spacer(1, 0.3 * inch))

        # Author
        self.story.append(Paragraph(f'by {author}', self.styles['CoverAuthor']))

        # Bottom spacing
        self.story.append(Spacer(1, 4 * inch))

        # Metadata
        metadata_parts = []
        if genre:
            metadata_parts.append(f'Genre: {genre}')
        if word_count:
            metadata_parts.append(f'Word Count: {word_count:,}')

        if metadata_parts:
            metadata_text = ' | '.join(metadata_parts)
            self.story.append(Paragraph(metadata_text, self.styles['Metadata']))

        # Page break
        self.story.append(PageBreak())

    def add_chapter(
        self,
        title: str,
        content: str,
        chapter_number: Optional[int] = None
    ):
        """Add a chapter with proper formatting"""
        # Chapter heading
        if chapter_number:
            heading_text = f'CHAPTER {chapter_number}<br/>{title}'
        else:
            heading_text = title

        self.story.append(Paragraph(heading_text, self.styles['ChapterHeading']))

        # Process content - handle scene breaks
        scenes = content.split('\n\n###\n\n')

        for i, scene in enumerate(scenes):
            # Add scene separator (except for first scene)
            if i > 0:
                self.story.append(Paragraph('###', self.styles['SceneBreak']))

            # Add scene paragraphs
            paragraphs = scene.strip().split('\n\n')
            for j, para_text in enumerate(paragraphs):
                if para_text.strip():
                    # First paragraph of scene has no indent
                    if i > 0 and j == 0:
                        style = self.styles['FirstParagraph']
                    else:
                        style = self.styles['BodyText']

                    # Escape XML entities for ReportLab
                    para_text = para_text.replace('&', '&amp;')
                    para_text = para_text.replace('<', '&lt;')
                    para_text = para_text.replace('>', '&gt;')

                    self.story.append(Paragraph(para_text.strip(), style))

        # Page break after chapter
        self.story.append(PageBreak())

    def add_front_matter(self, content: str, title: str = "Prologue"):
        """Add prologue or other front matter"""
        self.story.append(Paragraph(title, self.styles['ChapterHeading']))

        paragraphs = content.strip().split('\n\n')
        for i, para_text in enumerate(paragraphs):
            if para_text.strip():
                style = self.styles['FirstParagraph'] if i == 0 else self.styles['BodyText']

                para_text = para_text.replace('&', '&amp;')
                para_text = para_text.replace('<', '&lt;')
                para_text = para_text.replace('>', '&gt;')

                self.story.append(Paragraph(para_text.strip(), style))

        self.story.append(PageBreak())

    def build(self) -> bytes:
        """Build the PDF and return as bytes"""
        self.doc.build(self.story, canvasmaker=NumberedCanvas)
        self.buffer.seek(0)
        return self.buffer.getvalue()

    def save(self, output_path: str):
        """Save PDF to file"""
        with open(output_path, 'wb') as f:
            f.write(self.build())


def generate_manuscript_pdf(
    project_title: str,
    author_name: str,
    chapters: List[Dict[str, Any]],
    genre: Optional[str] = None,
    prologue: Optional[str] = None,
    epilogue: Optional[str] = None
) -> bytes:
    """
    Generate complete manuscript PDF

    Args:
        project_title: Book title
        author_name: Author name
        chapters: List of chapter dicts with 'title', 'content', 'number'
        genre: Optional genre
        prologue: Optional prologue text
        epilogue: Optional epilogue text

    Returns:
        PDF file as bytes
    """
    generator = PdfGenerator()

    # Calculate word count
    total_words = 0
    for chapter in chapters:
        content = chapter.get('content', '')
        total_words += len(content.split())

    # Cover page
    generator.add_cover_page(
        title=project_title,
        author=author_name,
        genre=genre,
        word_count=total_words
    )

    # Prologue
    if prologue:
        generator.add_front_matter(prologue, 'Prologue')

    # Chapters
    for i, chapter in enumerate(chapters):
        generator.add_chapter(
            title=chapter.get('title', 'Untitled'),
            content=chapter.get('content', ''),
            chapter_number=chapter.get('number', i + 1)
        )

    # Epilogue
    if epilogue:
        generator.add_front_matter(epilogue, 'Epilogue')

    return generator.build()
