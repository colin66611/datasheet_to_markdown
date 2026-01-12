"""Markdown Converter - Convert various content types to Markdown format"""

from typing import List, Optional, Tuple
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class MarkdownConverter:
    """Markdown Converter"""

    def __init__(self):
        self.logger = logger

    def heading_to_markdown(self, text: str, level: int) -> str:
        """
        Convert heading to Markdown

        Args:
            text: heading text
            level: heading level (1-6)

        Returns:
            Markdown formatted heading
        """
        if level < 1 or level > 6:
            level = 2

        prefix = "#" * level
        return f"{prefix} {text}\n\n"

    def paragraph_to_markdown(self, text: str) -> str:
        """
        Convert paragraph to Markdown

        Args:
            text: paragraph text

        Returns:
            Markdown formatted paragraph
        """
        if not text:
            return ""

        # Clean text
        cleaned = text.strip()

        return f"{cleaned}\n\n"

    def list_to_markdown(self, items: List[str], ordered: bool = False) -> str:
        """
        Convert list to Markdown

        Args:
            items: list items
            ordered: whether it's an ordered list

        Returns:
            Markdown formatted list
        """
        if not items:
            return ""

        lines = []
        for i, item in enumerate(items):
            if ordered:
                # Ordered list: 1. Item
                prefix = f"{i + 1}."
            else:
                # Unordered list: - Item
                prefix = "-"

            # Clean list item markers (if already present)
            cleaned_item = item.strip()
            # Remove leading •, -, *, ·, etc.
            for marker in ["•", "-", "*", "·"]:
                if cleaned_item.startswith(marker):
                    cleaned_item = cleaned_item[1:].strip()
                    break

            # Remove leading number + dot (if it's an ordered list)
            if ordered:
                import re
                match = re.match(r'^\d+[\.\)]\s+(.+)$', cleaned_item)
                if match:
                    cleaned_item = match.group(1)

            lines.append(f"{prefix} {cleaned_item}")

        return "\n".join(lines) + "\n\n"

    def table_to_markdown(self, table_data: List[List[str]],
                         caption: Optional[str] = None,
                         manual_check: bool = False,
                         uncertain_cells: List[Tuple[int, int]] = None) -> str:
        """
        Convert table to Markdown

        Args:
            table_data: table data (2D list)
            caption: table caption
            manual_check: whether manual verification is needed
            uncertain_cells: uncertain cell coordinates

        Returns:
            Markdown formatted table
        """
        if not table_data or not table_data[0]:
            return ""

        # Deep copy table data to avoid modifying original
        import copy
        table_data = copy.deepcopy(table_data)

        # Clean cell contents: remove newlines and extra spaces
        for row_idx, row in enumerate(table_data):
            for col_idx in range(len(row)):
                if row[col_idx]:
                    # Remove newlines, replace with spaces
                    cell = str(row[col_idx])
                    cell = cell.replace('\n', ' ').replace('\r', ' ')
                    # Remove extra spaces
                    cell = ' '.join(cell.split())
                    table_data[row_idx][col_idx] = cell

        # Mark uncertain cells
        if uncertain_cells:
            cell_set = set(uncertain_cells)
            for row_idx, row in enumerate(table_data):
                for col_idx in range(len(row)):
                    if (row_idx, col_idx) in cell_set:
                        cell = table_data[row_idx][col_idx]
                        # Mark empty cells as well, append marker for non-empty cells
                        if cell and cell.strip():
                            table_data[row_idx][col_idx] = f"{cell} [UNCERTAIN]"
                        else:
                            table_data[row_idx][col_idx] = "[UNCERTAIN]"

        # Find maximum column count (handle incomplete pdfplumber extraction)
        max_cols = max(len(row) for row in table_data)

        # Ensure all rows have same number of columns
        for row in table_data:
            while len(row) < max_cols:
                row.append("")

        # Remove completely empty columns (check from right to left)
        has_data = [False] * max_cols
        for row in table_data:
            for col_idx, cell in enumerate(row):
                if cell and cell.strip() and cell.strip() not in ['', '[UNCERTAIN]']:
                    has_data[col_idx] = True

        # Find the last column with data
        last_valid_col = max(i for i, data in enumerate(has_data) if data)

        # Truncate to valid columns
        if last_valid_col < max_cols - 1:
            table_data = [[row[i] for i in range(last_valid_col + 1)] for row in table_data]

        # Generate Markdown table
        lines = []

        # Table header
        header = table_data[0]
        lines.append("| " + " | ".join(str(cell) for cell in header) + " |")

        # Separator line
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")

        # Data rows
        for row in table_data[1:]:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        result = "\n".join(lines) + "\n\n"

        # Add caption
        if caption:
            caption_prefix = ""
            if manual_check:
                caption_prefix = " [MANUAL_CHECK]"

            result = f"### {caption}{caption_prefix}\n\n{result}"

        return result

    def image_to_markdown(self, image_path: str, alt: Optional[str] = None) -> str:
        """
        Convert image to Markdown

        Args:
            image_path: image path
            alt: alt text

        Returns:
            Markdown formatted image
        """
        if not alt:
            alt = "Image"

        return f"![{alt}]({image_path})\n\n"

    def code_to_markdown(self, code: str, language: str = "") -> str:
        """
        Convert code block to Markdown

        Args:
            code: code content
            language: language identifier

        Returns:
            Markdown formatted code block
        """
        return f"```{language}\n{code}\n```\n\n"

    def horizontal_rule(self) -> str:
        """Generate horizontal rule"""
        return "---\n\n"
