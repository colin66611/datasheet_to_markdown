"""Confidence Analyzer - Perform confidence scoring on extracted content"""

from typing import List, Tuple, Dict
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConfidenceScorer:
    """Confidence Analyzer"""

    def __init__(self, threshold: float = 50):
        """
        Initialize confidence analyzer

        Args:
            threshold: Suspicion threshold (0-100), above this value marked as suspicious
        """
        self.threshold = threshold
        self.logger = logger

    def score_table(self, table_data: List[List[str]], flask: float) -> Dict:
        """
        Perform confidence scoring on table

        Args:
            table_data: table data
            flask: camelot accuracy score

        Returns:
            Scoring result:
            {
                "overall_confidence": 0.0-100,
                "cell_confidence": [[0.9, 0.8, 0.95], ...],
                "uncertain_cells": [(1, 2), (3, 0)],
                "issues": ["Empty cell at (1,2)", "Truncated text at (3,0)"]
            }
        """
        if not table_data or not table_data[0]:
            return {
                "overall_confidence": 0.0,
                "cell_confidence": [],
                "uncertain_cells": [],
                "issues": []
            }

        rows = len(table_data)
        cols = len(table_data[0])
        cell_confidence = []
        uncertain_cells = []
        issues = []

        # Score each cell individually
        for row_idx, row in enumerate(table_data):
            row_scores = []
            for col_idx, cell in enumerate(row):
                score = self._score_cell(cell)
                row_scores.append(score)

                if score < self.threshold:
                    uncertain_cells.append((row_idx, col_idx))
                    issues.append(f"Low confidence ({score:.1f}) at ({row_idx},{col_idx})")

            cell_confidence.append(row_scores)

        # Calculate overall confidence
        flat_scores = [score for row in cell_confidence for score in row]
        overall = sum(flat_scores) / len(flat_scores) if flat_scores else 0.0

        # Combine with camelot's flask score
        overall = (overall + flask) / 2

        self.logger.debug(f"Table confidence: {overall:.2f}, uncertain cells: {len(uncertain_cells)}")

        return {
            "overall_confidence": overall,
            "cell_confidence": cell_confidence,
            "uncertain_cells": uncertain_cells,
            "issues": issues
        }

    def _score_cell(self, cell: str) -> float:
        """
        Score a cell

        Rules:
        - Empty cell: 0 points
        - Truncated text: 20 points
        - Normal text: 100 points
        """
        if not cell or str(cell).strip() == "":
            return 0.0

        cell_str = str(cell)

        if self._is_truncated(cell_str):
            return 20.0

        return 100.0

    def _is_truncated(self, text: str) -> bool:
        """
        Detect truncated text

        Rules:
        - Contains "..."
        - Ends with "<" or ">"
        - Contains "(continued)"
        """
        indicators = ["...", "(continued)", "(Continued)"]

        for ind in indicators:
            if ind in text:
                return True

        # Ends with < or >
        if text.endswith("<") or text.endswith(">"):
            return True

        return False

    def analyze_table_complexity(self, table_data: List[List[str]]) -> Dict:
        """
        Analyze table complexity

        Args:
            table_data: table data

        Returns:
            Complexity analysis:
            {
                "rows": 34,
                "cols": 7,
                "has_empty": True,
                "complexity_score": 0.85
            }
        """
        if not table_data:
            return {"rows": 0, "cols": 0, "has_empty": False, "complexity_score": 0.0}

        rows = len(table_data)
        cols = len(table_data[0]) if table_data else 0

        # Check for empty cells
        empty_count = 0
        total_cells = rows * cols

        for row in table_data:
            for cell in row:
                if not cell or str(cell).strip() == "":
                    empty_count += 1

        has_empty = empty_count > 0

        # Complexity score (0-1)
        # Large tables and many empty cells increase complexity
        size_complexity = min((rows * cols) / 200, 1.0)  # Maximum 200 cells
        empty_complexity = min(empty_count / total_cells, 1.0) if total_cells > 0 else 0

        complexity_score = (size_complexity + empty_complexity) / 2

        return {
            "rows": rows,
            "cols": cols,
            "has_empty": has_empty,
            "empty_count": empty_count,
            "complexity_score": complexity_score
        }

    def needs_manual_check(self, complexity: Dict, flask: float,
                          uncertain_ratio: float) -> bool:
        """
        Determine if manual verification is needed

        Trigger conditions (any one met):
        - Rows > 20 or Columns > 6
        - flask < 80
        - Uncertain cell ratio > 50%

        Args:
            complexity: complexity analysis
            flask: accuracy score
            uncertain_ratio: uncertain cell ratio

        Returns:
            True indicates manual verification is needed
        """
        # Condition 1: Table size too large
        if complexity.get("rows", 0) > 20 or complexity.get("cols", 0) > 6:
            return True

        # Condition 2: Low accuracy
        if flask < 80:
            return True

        # Condition 3: High uncertain cell ratio
        if uncertain_ratio > 0.5:
            return True

        return False
