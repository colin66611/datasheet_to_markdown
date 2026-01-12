"""Text extractor"""

from typing import List, Any
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class TextExtractor:
    """Text extractor"""

    def __init__(self):
        self.logger = logger

    def extract(self, page: Any, exclude_regions: List[tuple] = None) -> str:
        """
        Extract text

        Args:
            page: pdfplumber page object
            exclude_regions: List of exclusion regions [(x0, y0, x1, y1), ...]

        Returns:
            Extracted text
        """
        try:
            # Simplified implementation: directly use page.extract_text()
            text = page.extract_text()

            if text:
                # Clean text
                text = self._clean_text(text)

            return text or ""

        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """Clean text"""
        # Remove excessive blank lines
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)

        return "\n".join(cleaned_lines)
