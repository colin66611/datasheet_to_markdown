"""Manual Intervention Marker"""

from typing import List, Tuple
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ManualMarker:
    """Manual Intervention Marker"""

    def __init__(self):
        self.logger = logger

    def mark_table(self, table_data: List[List[str]],
                  uncertain_cells: List[Tuple[int, int]]) -> List[List[str]]:
        """
        Mark content in table that needs manual verification

        Rules:
        - Cell level: append [UNCERTAIN] to uncertain cell content

        Args:
            table_data: table data
            uncertain_cells: list of uncertain cell coordinates

        Returns:
            Marked table data
        """
        if not uncertain_cells:
            return table_data

        marked_table = []

        for row_idx, row in enumerate(table_data):
            marked_row = []
            for col_idx, cell in enumerate(row):
                cell_str = str(cell) if cell is not None else ""

                # Check if it's an uncertain cell
                if (row_idx, col_idx) in uncertain_cells:
                    cell_str = f"{cell_str} [UNCERTAIN]"

                marked_row.append(cell_str)

            marked_table.append(marked_row)

        self.logger.debug(f"Marked {len(uncertain_cells)} uncertain cells")
        return marked_table

    def mark_text(self, text: str, issues: List[str]) -> str:
        """
        Mark content in text that needs manual verification

        Args:
            text: text content
            issues: list of issues

        Returns:
            Marked text
        """
        if not issues:
            return text

        # Append warning marker after text
        marked = f"{text}\n\n<!-- Issues: {', '.join(issues)} -->"

        return marked

    def add_table_marker(self, markdown: str, needs_check: bool) -> str:
        """
        Add manual verification marker after table caption

        Args:
            markdown: original markdown text
            needs_check: whether manual verification is needed

        Returns:
            Markdown with added marker
        """
        if needs_check:
            # Add [MANUAL_CHECK] after table caption or description
            if markdown.strip().startswith("|"):
                # If it's directly a table, add comment before it
                return f"<!-- [MANUAL_CHECK] This table requires manual verification -->\n\n{markdown}"
            else:
                # If there's a caption, add marker after caption
                return f"{markdown} [MANUAL_CHECK]"

        return markdown
