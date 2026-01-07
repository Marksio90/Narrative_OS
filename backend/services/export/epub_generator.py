"""
EPUB Export Generator
Professional ebook formatting for EPUB3 standard
Uses ebooklib for modern EPUB generation
"""
from ebooklib import epub
from typing import Optional, List, Dict, Any
from datetime import datetime
import io


class EpubGenerator:
    """
    Generate EPUB3 ebooks

    Features:
    - EPUB3 standard compliance
    - Responsive typography
    - Chapter navigation
    - Metadata (title, author, language, ISBN)
    - Cover image support
    - CSS styling for consistent reading experience
    """

    def __init__(
        self,
        title: str,
        author: str,
        language: str = 'en',
        identifier: Optional[str] = None
    ):
        self.book = epub.EpubBook()

        # Set metadata
        self.book.set_title(title)
        self.book.set_language(language)
        self.book.add_author(author)

        # Unique identifier (use ISBN or generate)
        if identifier:
            self.book.set_identifier(identifier)
        else:
            # Generate identifier from title and timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.book.set_identifier(f'narrative-os-{timestamp}')

        self.chapters = []
        self.spine = ['nav']

    def add_cover(self, image_path: str):
        """Add cover image (JPEG or PNG)"""
        with open(image_path, 'rb') as f:
            self.book.set_cover('cover.jpg', f.read())

    def add_metadata(
        self,
        publisher: Optional[str] = None,
        description: Optional[str] = None,
        rights: Optional[str] = None,
        genre: Optional[str] = None
    ):
        """Add additional metadata"""
        if publisher:
            self.book.add_metadata('DC', 'publisher', publisher)
        if description:
            self.book.add_metadata('DC', 'description', description)
        if rights:
            self.book.add_metadata('DC', 'rights', rights)
        if genre:
            self.book.add_metadata('DC', 'subject', genre)

        # Publication date
        self.book.add_metadata(
            'DC',
            'date',
            datetime.now().strftime('%Y-%m-%d')
        )

    def add_chapter(
        self,
        title: str,
        content: str,
        filename: Optional[str] = None
    ) -> epub.EpubHtml:
        """
        Add a chapter to the ebook

        Args:
            title: Chapter title
            content: Chapter HTML or plain text
            filename: Optional custom filename (auto-generated if None)

        Returns:
            EpubHtml chapter object
        """
        # Generate filename
        if not filename:
            chapter_num = len(self.chapters) + 1
            filename = f'chapter_{chapter_num}.xhtml'

        # Create chapter
        chapter = epub.EpubHtml(
            title=title,
            file_name=filename,
            lang='en'
        )

        # Convert plain text to HTML if needed
        if not content.strip().startswith('<'):
            content = self._text_to_html(content)

        chapter.content = content
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        self.spine.append(chapter)

        return chapter

    def _text_to_html(self, text: str) -> str:
        """
        Convert plain text to HTML
        Handles paragraphs and scene breaks
        """
        html = '<html><head></head><body>\n'

        # Split by scene breaks
        scenes = text.split('\n\n###\n\n')

        for i, scene in enumerate(scenes):
            # Add scene separator
            if i > 0:
                html += '<p style="text-align: center; margin: 2em 0;">* * *</p>\n'

            # Split into paragraphs
            paragraphs = scene.strip().split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # Escape HTML entities
                    para = para.replace('&', '&amp;')
                    para = para.replace('<', '&lt;')
                    para = para.replace('>', '&gt;')
                    html += f'<p>{para.strip()}</p>\n'

        html += '</body></html>'
        return html

    def add_css(self, custom_css: Optional[str] = None):
        """Add CSS stylesheet for consistent styling"""
        if custom_css:
            css = custom_css
        else:
            # Default professional ebook CSS
            css = '''
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 1.1em;
    line-height: 1.6;
    margin: 0 1em;
    text-align: justify;
}

h1, h2, h3 {
    font-family: "Helvetica Neue", "Arial", sans-serif;
    font-weight: bold;
    text-align: center;
    margin-top: 2em;
    margin-bottom: 1em;
    page-break-after: avoid;
}

h1 {
    font-size: 2em;
    margin-top: 3em;
}

h2 {
    font-size: 1.5em;
}

p {
    margin: 0;
    text-indent: 1.5em;
    orphans: 2;
    widows: 2;
}

p:first-of-type {
    text-indent: 0;
}

p.no-indent {
    text-indent: 0;
}

p.scene-break {
    text-align: center;
    text-indent: 0;
    margin: 2em 0;
    font-size: 1.2em;
}

.center {
    text-align: center;
    text-indent: 0;
}

.chapter-title {
    font-size: 1.8em;
    font-weight: bold;
    text-align: center;
    margin: 3em 0 2em 0;
    page-break-before: always;
}
'''

        # Create CSS file
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=css
        )
        self.book.add_item(nav_css)

        # Apply CSS to all chapters
        for chapter in self.chapters:
            chapter.add_link(href='style/nav.css', rel='stylesheet', type='text/css')

    def finalize(self):
        """Finalize the book (add TOC, spine, etc.)"""
        # Create table of contents
        self.book.toc = tuple(self.chapters)

        # Add navigation files
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # Define spine (reading order)
        self.book.spine = self.spine

    def to_bytes(self) -> bytes:
        """Return EPUB as bytes for download"""
        buffer = io.BytesIO()
        epub.write_epub(buffer, self.book)
        buffer.seek(0)
        return buffer.getvalue()

    def save(self, output_path: str):
        """Save EPUB to file"""
        epub.write_epub(output_path, self.book)


def generate_manuscript_epub(
    project_title: str,
    author_name: str,
    chapters: List[Dict[str, Any]],
    genre: Optional[str] = None,
    prologue: Optional[str] = None,
    epilogue: Optional[str] = None,
    description: Optional[str] = None,
    cover_image_path: Optional[str] = None
) -> bytes:
    """
    Generate complete manuscript EPUB

    Args:
        project_title: Book title
        author_name: Author name
        chapters: List of chapter dicts with 'title', 'content'
        genre: Optional genre for metadata
        prologue: Optional prologue text
        epilogue: Optional epilogue text
        description: Optional book description
        cover_image_path: Optional path to cover image

    Returns:
        EPUB file as bytes
    """
    generator = EpubGenerator(
        title=project_title,
        author=author_name
    )

    # Add metadata
    generator.add_metadata(
        publisher='Narrative OS',
        description=description or f'A novel by {author_name}',
        genre=genre,
        rights=f'© {datetime.now().year} {author_name}. All rights reserved.'
    )

    # Add cover if provided
    if cover_image_path:
        try:
            generator.add_cover(cover_image_path)
        except Exception:
            pass  # Skip if cover fails

    # Add title page
    title_html = f'''
    <html>
    <head><title>{project_title}</title></head>
    <body>
        <div style="text-align: center; margin-top: 40%;">
            <h1>{project_title}</h1>
            <p style="font-size: 1.2em; margin-top: 2em;">by {author_name}</p>
        </div>
    </body>
    </html>
    '''
    title_chapter = epub.EpubHtml(
        title='Title Page',
        file_name='title.xhtml',
        lang='en'
    )
    title_chapter.content = title_html
    generator.book.add_item(title_chapter)
    generator.spine.append(title_chapter)

    # Prologue
    if prologue:
        generator.add_chapter('Prologue', prologue, 'prologue.xhtml')

    # Chapters
    for i, chapter in enumerate(chapters):
        title = chapter.get('title', f'Chapter {i+1}')
        content = chapter.get('content', '')

        # Wrap title in H1 for chapter
        html_content = f'<h1 class="chapter-title">{title}</h1>\n'
        html_content += generator._text_to_html(content)

        generator.add_chapter(
            title=title,
            content=html_content,
            filename=f'chapter_{i+1}.xhtml'
        )

    # Epilogue
    if epilogue:
        generator.add_chapter('Epilogue', epilogue, 'epilogue.xhtml')

    # Add CSS styling
    generator.add_css()

    # Finalize
    generator.finalize()

    return generator.to_bytes()
