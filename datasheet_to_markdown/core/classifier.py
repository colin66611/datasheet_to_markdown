"""Content Block Classifier - Core Module

Responsible for classifying PDF page content into different content blocks:
- Heading (HEADING)
- Paragraph (PARAGRAPH)
- List (LIST)
- Table (TABLE)
- Image (IMAGE)
- Footer (FOOTER) - needs to be filtered
- Page Number (PAGE_NUMBER) - needs to be filtered
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Dict
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentType(Enum):
    """Content Type Enumeration"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    FOOTER = "footer"
    PAGE_NUMBER = "page_number"


@dataclass
class ContentBlock:
    """Content Block Data Structure"""
    type: ContentType
    content: Any
    page_num: int
    bbox: tuple  # (x0, y0, x1, y1)
    metadata: Dict = field(default_factory=dict)

    # Heading-specific properties
    heading_level: Optional[int] = None

    # List-specific properties
    list_ordered: bool = False
    list_items: List[str] = field(default_factory=list)

    # Table-specific properties
    table_shape: Optional[tuple] = None  # (rows, cols)
    table_flask: Optional[float] = None  # camelot accuracy score

    # Image-specific properties
    image_path: Optional[str] = None

    # Confidence-related
    needs_manual_check: bool = False
    uncertain_cells: List[tuple] = field(default_factory=list)


class ContentBlockClassifier:
    """Content Block Classifier - Core Class"""

    # Section number regex patterns (sorted by priority)
    SECTION_PATTERNS = [
        (r'^(\d+)\.(\d+)\.(\d+)\s+(.+)$', 3),  # "3.1.2 Subsection" → Level 3
        (r'^(\d+)\.(\d+)\.\s+(.+)$', 2),      # "2.1 Description" → Level 2
        (r'^(\d+)\.\s+(.+)$', 1),             # "1. Features" → Level 1
        (r'^([A-Z][A-Z\s\d]+)$', 2),          # "FEATURES" → Level 2
    ]

    def __init__(self, page: Any, page_num: int, page_height: float):
        """
        Initialize classifier

        Args:
            page: pdfplumber page object
            page_num: page number
            page_height: page height
        """
        self.page = page
        self.page_num = page_num
        self.page_height = page_height
        self.logger = logger

    def classify(self) -> List[ContentBlock]:
        """
        Classify page content into multiple content blocks

        Returns:
            List of ContentBlocks, sorted from top to bottom of the page
        """
        blocks = []

        # 1. Extract text blocks
        text_blocks = self._extract_text_blocks()
        blocks.extend(text_blocks)

        # 2. Extract images (using pdfplumber)
        images = self._extract_images()
        blocks.extend(images)

        # 3. Sort by position (top to bottom, y-coordinate descending)
        blocks.sort(key=lambda b: b.bbox[1], reverse=True)

        # 4. Filter out headers, footers, and page numbers
        blocks = [b for b in blocks if not self._is_footer(b)]

        self.logger.debug(f"Page {self.page_num}: Classified {len(blocks)} content blocks")

        return blocks

    def _extract_text_blocks(self) -> List[ContentBlock]:
        """Extract text blocks"""
        blocks = []
        words = self.page.extract_words()

        if not words:
            return blocks

        # Group words into text lines by position
        lines = self._group_words_to_lines(words)

        for line_words in lines:
            if not line_words:
                continue

            # Merge into text
            text = " ".join([w["text"] for w in line_words])
            text = text.strip()

            if not text:
                continue

            # Calculate bounding box
            x0 = min(w["x0"] for w in line_words)
            y0 = min(w["top"] for w in line_words)
            x1 = max(w["x1"] for w in line_words)
            y1 = max(w["bottom"] for w in line_words)

            # Determine content type
            content_type, metadata = self._classify_text_type(text, line_words)

            # Create content block
            if content_type == ContentType.HEADING:
                level = self._extract_heading_level(text)
                block = ContentBlock(
                    type=content_type,
                    content=text,
                    page_num=self.page_num,
                    bbox=(x0, y0, x1, y1),
                    metadata=metadata,
                    heading_level=level
                )
            elif content_type == ContentType.LIST:
                block = ContentBlock(
                    type=content_type,
                    content=text,
                    page_num=self.page_num,
                    bbox=(x0, y0, x1, y1),
                    metadata=metadata,
                    list_ordered=metadata.get("ordered", False),
                    list_items=[text]
                )
            else:  # PARAGRAPH
                block = ContentBlock(
                    type=content_type,
                    content=text,
                    page_num=self.page_num,
                    bbox=(x0, y0, x1, y1),
                    metadata=metadata
                )

            blocks.append(block)

        return blocks

    def _group_words_to_lines(self, words: List[Dict]) -> List[List[Dict]]:
        """Group words into lines"""
        if not words:
            return []

        # Sort by y-coordinate
        words_sorted = sorted(words, key=lambda w: w["top"])

        lines = []
        current_line = [words_sorted[0]]
        current_y = words_sorted[0]["top"]
        y_threshold = 5  # y-coordinate tolerance

        for word in words_sorted[1:]:
            if abs(word["top"] - current_y) <= y_threshold:
                current_line.append(word)
            else:
                # Sort current line by x-coordinate
                lines.append(sorted(current_line, key=lambda w: w["x0"]))
                current_line = [word]
                current_y = word["top"]

        # Add last line
        if current_line:
            lines.append(sorted(current_line, key=lambda w: w["x0"]))

        return lines

    def _classify_text_type(self, text: str, words: List[Dict]) -> tuple:
        """
        Classify text type

        Returns:
            (ContentType, metadata)
        """
        # Check if it's a heading
        if self._is_heading(text, words):
            return ContentType.HEADING, {"confidence": 0.95}

        # Check if it's a list
        if self._is_list(text):
            ordered = text[0].isdigit()
            return ContentType.LIST, {"ordered": ordered}

        # Default to paragraph
        return ContentType.PARAGRAPH, {}

    def _is_heading(self, text: str, words: List[Dict]) -> bool:
        """
        Determine if text is a heading

        Rules:
        1. Regex match section number (priority)
        2. Font size larger than normal text (fallback)
        """
        # Rule 1: Regex match
        for pattern, _ in self.SECTION_PATTERNS:
            if re.match(pattern, text.strip()):
                return True

        # Rule 2: Font size (if font info available)
        if words and "size" in words[0]:
            avg_font_size = sum(w.get("size", 12) for w in words) / len(words)
            if avg_font_size > 14:  # Assume normal text font size ≤ 14
                return True

        return False

    def _is_list(self, text: str) -> bool:
        """
        Determine if text is a list

        Rules:
        - Starts with "•", "-", "*" → unordered list
        - Starts with number + dot → ordered list
        """
        stripped = text.strip()

        # Unordered list markers
        unordered_markers = ["•", "-", "*", "·"]
        if stripped[0] in unordered_markers if stripped else False:
            return True

        # Ordered list (starts with number)
        if re.match(r'^\d+[\.\)]\s+', stripped):
            return True

        return False

    def _is_footer(self, block: ContentBlock) -> bool:
        """
        Determine if content is header or footer

        Rules:
        - Appears in top or bottom 10% of page
        - Contains page numbers, company names, document titles, etc.
        """
        y0 = block.bbox[1]

        # Position rule: top 10% or bottom 10%
        if y0 > self.page_height * 0.9 or y0 < self.page_height * 0.1:
            # Content rule
            text = str(block.content).strip()

            # Pure numbers (page number)
            if re.match(r'^\s*\d+\s*$', text):
                return True

            # Contains "Page" or page number pattern
            if re.match(r'.*(page|页)\s*\d+.*', text, re.I):
                return True

            # "- X -" format page number
            if re.match(r'^\s*-\s*\d+\s*-\s*$', text):
                return True

            # All caps short text (possibly company name, repeats)
            if len(text) < 50 and text.isupper() and not block.type == ContentType.HEADING:
                # Simplified handling: non-heading all-caps short text might be header
                return True

        return False

    def _extract_heading_level(self, text: str) -> int:
        """
        Extract heading level

        Rules:
        - "1. Features" → Level 1 heading (#)
        - "2.1 Description" → Level 2 heading (##)
        - "3.1.2 Pin Functions" → Level 3 heading (###)
        """
        for pattern, level in self.SECTION_PATTERNS:
            match = re.match(pattern, text.strip())
            if match:
                return level

        # Default to level 2
        return 2

    def _extract_images(self) -> List[ContentBlock]:
        """
        Extract images (simplified version, actual image extraction in ImageExtractor)
        """
        # Simplified implementation: detect image regions on page
        images = []

        # pdfplumber images detection
        if hasattr(self.page, "images"):
            for img in self.page.images:
                # Image bounding box
                bbox = (
                    img.get("x0", 0),
                    img.get("y0", 0),
                    img.get("x1", 0),
                    img.get("y1", 0)
                )

                block = ContentBlock(
                    type=ContentType.IMAGE,
                    content=img,
                    page_num=self.page_num,
                    bbox=bbox,
                    metadata={"image_type": img.get("stream_type", "unknown")}
                )

                images.append(block)

        return images
