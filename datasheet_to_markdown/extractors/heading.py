"""Heading detector - specifically responsible for heading recognition and level extraction"""

import re
from typing import Optional, Dict
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class HeadingDetector:
    """Heading detector"""

    # Section number regex patterns
    SECTION_PATTERNS = [
        r'^(\d+)\.\s+(.+)$',           # "1. Features"
        r'^(\d+)\.(\d+)\.\s+(.+)$',    # "2.1 Description"
        r'^(\d+)\.(\d+)\.(\d+)\s+(.+)$',  # "3.1.2 Subsection"
        r'^([A-Z][A-Z\s\d]+)$',        # "FEATURES", "PIN CONFIGURATION"
    ]

    def __init__(self):
        self.logger = logger

    def detect(self, text: str, font_size: float = None) -> Optional[Dict]:
        """
        Detect if text is a heading

        Args:
            text: Text content
            font_size: Font size (optional)

        Returns:
            If it's a heading, returns:
            {
                "level": 1-6,
                "text": "Heading text",
                "confidence": 0.0-1.0
            }
            Otherwise returns None
        """
        # Prefer regex matching
        for pattern in self.SECTION_PATTERNS:
            match = re.match(pattern, text.strip())
            if match:
                level = self._extract_level_from_pattern(pattern, match)
                return {
                    "level": level,
                    "text": text.strip(),
                    "confidence": 0.95
                }

        # Alternative: judgment based on font size
        if font_size and font_size > 14:  # Assume regular text font ≤ 14
            return {
                "level": self._estimate_level_from_font(font_size),
                "text": text.strip(),
                "confidence": 0.7
            }

        return None

    def extract_level(self, text: str) -> int:
        """
        Extract level from heading text

        Args:
            text: Heading text

        Returns:
            Level (1-6)
        """
        for pattern in self.SECTION_PATTERNS:
            match = re.match(pattern, text.strip())
            if match:
                return self._extract_level_from_pattern(pattern, match)

        # Default level 2
        return 2

    def _extract_level_from_pattern(self, pattern: str, match: re.Match) -> int:
        """Extract level from regex match result"""
        # "1. Features" → Level 1
        if r'^(\d+)\.\s+' in pattern:
            return 1

        # "2.1 Description" → Level 2
        if r'^(\d+)\.(\d+)\.\s+' in pattern:
            return 2

        # "3.1.2 Subsection" → Level 3
        if r'^(\d+)\.(\d+)\.(\d+)\s+' in pattern:
            return 3

        # All-caps heading → Level 2
        if r'^([A-Z][A-Z\s\d]+)$' in pattern:
            return 2

        return 2

    def _estimate_level_from_font(self, font_size: float) -> int:
        """Estimate level based on font size"""
        if font_size >= 20:
            return 1
        elif font_size >= 16:
            return 2
        elif font_size >= 14:
            return 3
        else:
            return 4
