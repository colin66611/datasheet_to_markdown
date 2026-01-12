"""Document Builder - Assembles complete Markdown documents"""

from typing import List, Optional
from .converters.markdown import MarkdownConverter
from .converters.marker import ManualMarker
from .core.classifier import ContentBlock, ContentType
from .utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentBuilder:
    """Document Builder"""

    def __init__(self, title: str = None, add_toc: bool = False):
        """
        Initialize document builder

        Args:
            title: Document title
            add_toc: Whether to add table of contents
        """
        self.title = title or "Document"
        self.add_toc = add_toc
        self.converter = MarkdownConverter()
        self.marker = ManualMarker()
        self.content_parts = []
        self.headings = []
        self.logger = logger

    def add_heading(self, text: str, level: int):
        """
        Add heading

        Args:
            text: Heading text
            level: Level (1-6)
        """
        markdown = self.converter.heading_to_markdown(text, level)
        self.content_parts.append(markdown)

        # Record heading for TOC generation
        self.headings.append({
            "level": level,
            "text": text
        })

        self.logger.debug(f"Added heading: {'#' * level} {text}")

    def add_paragraph(self, text: str):
        """Add paragraph"""
        markdown = self.converter.paragraph_to_markdown(text)
        self.content_parts.append(markdown)
        self.logger.debug(f"Added paragraph: {text[:50]}...")

    def add_list(self, items: List[str], ordered: bool = False):
        """
        Add list

        Args:
            items: List items
            ordered: Whether it's an ordered list
        """
        markdown = self.converter.list_to_markdown(items, ordered)
        self.content_parts.append(markdown)
        self.logger.debug(f"Added list: {len(items)} items")

    def add_table(self, table_data: List[List[str]],
                  caption: str = None,
                  manual_check: bool = False,
                  uncertain_cells: List[tuple] = None):
        """
        Add table

        Args:
            table_data: Table data
            caption: Table caption
            manual_check: Whether to mark as needing manual review
            uncertain_cells: Coordinates of uncertain cells
        """
        markdown = self.converter.table_to_markdown(
            table_data, caption, manual_check, uncertain_cells
        )
        self.content_parts.append(markdown)
        self.logger.debug(
            f"Added table: {len(table_data)} rows × {len(table_data[0]) if table_data else 0} cols, "
            f"manual_check={'yes' if manual_check else 'no'}"
        )

    def add_image(self, path: str, alt: str = None):
        """
        Add image reference

        Args:
            path: Image path
            alt: Alt text
        """
        markdown = self.converter.image_to_markdown(path, alt)
        self.content_parts.append(markdown)
        self.logger.debug(f"Added image: {path}")

    def add_raw(self, text: str):
        """Add raw text"""
        self.content_parts.append(text)

    def add_toc(self):
        """Add table of contents"""
        if not self.headings:
            return

        toc_lines = ["## Table of Contents\n\n"]

        for heading in self.headings:
            # Generate anchor
            anchor = heading["text"].lower().replace(" ", "-").replace(".", "")
            # Indent based on level
            indent = "  " * (heading["level"] - 1)
            toc_lines.append(f"{indent}- [{heading['text']}](#{anchor})")

        toc_lines.append("\n")
        self.content_parts.insert(0, "\n".join(toc_lines))
        self.logger.debug(f"Added TOC: {len(self.headings)} headings")

    def build(self) -> str:
        """
        Build complete Markdown document

        Returns:
            Markdown string
        """
        # Add document title
        document = f"# {self.title}\n\n"

        # Add TOC (if needed)
        if self.add_toc and self.headings:
            toc_parts = self._build_toc()
            document += toc_parts + "\n"

        # Add all content
        document += "".join(self.content_parts)

        return document

    def _build_toc(self) -> str:
        """Build table of contents"""
        toc_lines = ["## Table of Contents\n\n"]

        for heading in self.headings:
            # Generate anchor
            anchor = heading["text"].lower().replace(" ", "-").replace(".", "")
            # Indent based on level
            indent = "  " * (heading["level"] - 1)
            toc_lines.append(f"{indent}- [{heading['text']}](#{anchor})")

        toc_lines.append("\n" + self.converter.horizontal_rule())

        return "\n".join(toc_lines)

    def get_stats(self) -> dict:
        """Get document statistics"""
        stats = {
            "total_headings": len(self.headings),
            "headings_by_level": {},
            "total_parts": len(self.content_parts)
        }

        for heading in self.headings:
            level = heading["level"]
            stats["headings_by_level"][level] = \
                stats["headings_by_level"].get(level, 0) + 1

        return stats
