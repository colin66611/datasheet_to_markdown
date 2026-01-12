"""List extractor"""

from typing import List, Dict
import re
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ListExtractor:
    """List extractor"""

    def __init__(self):
        self.logger = logger

    def extract(self, text_blocks: List[str]) -> List[Dict]:
        """
        Extract lists

        Args:
            text_blocks: List of text blocks

        Returns:
            List of list items:
            [
                {
                    "type": "ordered" or "unordered",
                    "items": ["Item 1", "Item 2", ...],
                    "indent": 0  # Indentation level
                }
            ]
        """
        if not text_blocks:
            return []

        result = []
        current_list = None

        for text in text_blocks:
            if self._is_list_item(text):
                list_type = self._get_list_type(text)

                if current_list is None or current_list["type"] != list_type:
                    # Start new list
                    if current_list:
                        result.append(current_list)

                    current_list = {
                        "type": list_type,
                        "items": [],
                        "indent": 0
                    }

                # Add to current list
                current_list["items"].append(text.strip())

            else:
                # Not a list item, end current list
                if current_list:
                    result.append(current_list)
                    current_list = None

        # Add the last list
        if current_list:
            result.append(current_list)

        return result

    def _is_list_item(self, text: str) -> bool:
        """
        Determine if text is a list item

        Args:
            text: Text content

        Returns:
            True if it's a list item
        """
        stripped = text.strip()

        # Unordered list markers
        unordered_markers = ["•", "-", "*", "·"]
        if stripped and stripped[0] in unordered_markers:
            return True

        # Ordered list (numbered)
        if re.match(r'^\d+[\.\)]\s+', stripped):
            return True

        return False

    def _get_list_type(self, text: str) -> str:
        """
        Get list type

        Args:
            text: Text content

        Returns:
            "ordered" or "unordered"
        """
        stripped = text.strip()

        # Check if it's an ordered list
        if re.match(r'^\d+[\.\)]\s+', stripped):
            return "ordered"

        return "unordered"
