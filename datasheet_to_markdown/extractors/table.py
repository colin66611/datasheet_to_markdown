"""Table Extractor - Extract tables using pdfplumber (MVP simplified version)"""

import os
from typing import List, Dict, Optional, Any
from datasheet_to_markdown.core.scorer import ConfidenceScorer
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class TableExtractor:
    """Table Extractor (using pdfplumber as MVP implementation)"""

    def __init__(self, pdf_path: str, page_num: int,
                 confidence_threshold: float = 50):
        """
        Initialize table extractor

        Args:
            pdf_path: PDF file path
            page_num: page number (starting from 1)
            confidence_threshold: confidence threshold (0-100)
        """
        self.pdf_path = pdf_path
        self.page_num = page_num
        self.confidence_threshold = confidence_threshold
        self.scorer = ConfidenceScorer(threshold=confidence_threshold)
        self.logger = logger

    def extract(self, page: Any) -> List[Dict]:
        """
        Extract tables

        Args:
            page: pdfplumber page object

        Returns:
            List of tables:
            [
                {
                    "data": [["Header1", "Header2"], ["Data1", "Data2"]],
                    "flask": 85.5,  # Simulated accuracy score
                    "page": page_num,
                    "bbox": (x0, y0, x1, y1),
                    "needs_manual_check": False,
                    "uncertain_cells": [(0, 1), (2, 3)]
                }
            ]
        """
        tables = []

        try:
            # Use pdfplumber to extract tables
            extracted_tables = page.extract_tables()

            # Check return value type
            if not extracted_tables:
                return tables

            # If not a list, try to convert to list
            if not isinstance(extracted_tables, list):
                self.logger.warning(f"Page {self.page_num}: extract_tables returned non-list type: {type(extracted_tables)}")
                return tables

            self.logger.debug(f"Page {self.page_num}: Extracted {len(extracted_tables)} table(s)")

            # Process each table
            for i, table in enumerate(extracted_tables):
                # Skip non-table objects
                if not isinstance(table, list):
                    self.logger.warning(f"Page {self.page_num}: Table {i} is not a list type: {type(table)}")
                    continue

                table_dict = self._process_table(table, i)
                if table_dict:
                    tables.append(table_dict)

        except Exception as e:
            self.logger.warning(f"Page {self.page_num}: Table extraction failed - {e}")
            import traceback
            self.logger.debug(traceback.format_exc())

        return tables

    def _process_table(self, table_data: List[List[str]], index: int) -> Optional[Dict]:
        """Process a single table"""
        try:
            # Clean and filter table data
            filtered_data = []

            for row in table_data:
                # Clean each cell: remove newlines
                cleaned_row = []
                for cell in row:
                    if cell is None:
                        cleaned_row.append("")
                    else:
                        # Remove newlines, replace with spaces
                        cell_str = str(cell).replace('\n', ' ').replace('\r', ' ')
                        # Remove extra spaces
                        cell_str = ' '.join(cell_str.split())
                        cleaned_row.append(cell_str)

                # Only keep non-empty rows (at least one non-empty cell)
                if cleaned_row and any(cell.strip() for cell in cleaned_row):
                    filtered_data.append(cleaned_row)

            if not filtered_data:
                return None

            # Ensure all rows have the same number of columns
            max_cols = max(len(row) for row in filtered_data)
            for row in filtered_data:
                while len(row) < max_cols:
                    row.append("")

            # Remove completely empty columns on the right
            # Check if each column has data
            has_data = [False] * max_cols
            for row in filtered_data:
                for col_idx, cell in enumerate(row):
                    if cell and cell.strip():
                        has_data[col_idx] = True

            # Find the last column with data
            if any(has_data):
                last_valid_col = max(i for i, data in enumerate(has_data) if data)
                # Truncate to valid columns
                filtered_data = [[row[i] for i in range(last_valid_col + 1)] for row in filtered_data]

            # Simulate flask score (based on table completeness)
            total_cells = sum(len(row) for row in filtered_data)
            non_empty_cells = sum(sum(1 for cell in row if cell and cell.strip()) for row in filtered_data)
            flask = (non_empty_cells / total_cells * 100) if total_cells > 0 else 50

            # Confidence analysis
            score_result = self.scorer.score_table(filtered_data, flask)

            # Complexity analysis
            complexity = self.scorer.analyze_table_complexity(filtered_data)

            # Determine if manual verification is needed
            uncertain_ratio = len(score_result["uncertain_cells"]) / (complexity["rows"] * complexity["cols"]) if complexity["rows"] > 0 else 0
            needs_check = self.scorer.needs_manual_check(
                complexity, flask, uncertain_ratio
            )

            result = {
                "data": filtered_data,
                "flask": flask,
                "page": self.page_num,
                "index": index,
                "bbox": None,  # pdfplumber's extract_tables doesn't return bbox
                "needs_manual_check": needs_check,
                "uncertain_cells": score_result["uncertain_cells"],
                "complexity": complexity,
                "confidence": score_result["overall_confidence"]
            }

            self.logger.debug(
                f"Table {index}: {complexity['rows']} rows × {complexity['cols']} cols, "
                f"flask={flask:.2f}, manual check={'yes' if needs_check else 'no'}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to process table: {e}")
            return None
