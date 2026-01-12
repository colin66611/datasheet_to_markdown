"""Quality Reporter - Generate quality reports and output CLI warnings"""

from typing import List, Dict
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class QualityReporter:
    """Quality Reporter"""

    def __init__(self):
        self.tables_checked: List[Dict] = []
        self.total_tables: int = 0
        self.total_confidence: float = 0.0
        self.logger = logger

    def report_table(self, table_info: Dict):
        """
        Record table quality information

        Args:
            table_info:
            {
                "page_num": 4,
                "caption": "Pin Functions",
                "flask": 75.5,
                "needs_manual_check": True,
                "complexity": "high"
            }
        """
        self.tables_checked.append(table_info)
        self.total_tables += 1

        if "flask" in table_info:
            self.total_confidence += table_info["flask"]

    def print_summary(self):
        """
        Output CLI quality summary

        Example output:
        ⚠️  Warning: Detected 3 tables requiring manual verification
        ⚠️  Table 2 (Page 4): Pin Functions - Complexity: High
        💡  Search for [MANUAL_CHECK] in the generated Markdown to quickly locate

        📊  Quality Report:
        - Total tables: 75
        - Manual check required: 3 (4%)
        - Average confidence: 92.5%
        - Coverage: 99.2%
        """
        # Count tables requiring manual verification
        manual_check_tables = [t for t in self.tables_checked if t.get("needs_manual_check", False)]

        if manual_check_tables:
            print(f"\n⚠️  Warning: Detected {len(manual_check_tables)} table(s) requiring manual verification\n")

            for i, table in enumerate(manual_check_tables[:5], 1):  # Show at most 5
                page = table.get("page", "?")
                caption = table.get("caption", f"Table {i}")
                complexity = table.get("complexity", {})
                complexity_score = complexity.get("complexity_score", 0)

                if complexity_score > 0.7:
                    level = "High"
                elif complexity_score > 0.4:
                    level = "Medium"
                else:
                    level = "Low"

                print(f"⚠️  Table {i} (Page {page}): {caption} - Complexity: {level}")

            if len(manual_check_tables) > 5:
                print(f"... and {len(manual_check_tables) - 5} more table(s) need verification")

            print("\n💡  Search for [MANUAL_CHECK] in the generated Markdown to quickly locate\n")

        # Output quality report
        metrics = self.get_metrics()

        print("📊  Quality Report:")
        print(f"- Total tables: {metrics['total_tables']}")
        print(f"- Manual check required: {metrics['manual_check_tables']} "
              f"({metrics['manual_check_ratio'] * 100:.1f}%)")

        if metrics['avg_confidence'] > 0:
            print(f"- Average confidence: {metrics['avg_confidence']:.1f}%")

        print(f"- Coverage: {metrics['coverage']:.1f}%\n")

    def get_metrics(self) -> Dict:
        """
        Get quality metrics

        Returns:
            {
                "total_tables": 75,
                "manual_check_tables": 3,
                "manual_check_ratio": 0.04,
                "avg_confidence": 92.5,
                "coverage": 99.2
            }
        """
        manual_check_count = sum(1 for t in self.tables_checked
                                if t.get("needs_manual_check", False))

        avg_confidence = self.total_confidence / self.total_tables if self.total_tables > 0 else 0

        # Coverage calculation: (accurate fields + marked uncertain fields) / total fields
        # Simplified calculation: 100% - (uncertain cell ratio * confidence discount)
        total_uncertain = sum(len(t.get("uncertain_cells", [])) for t in self.tables_checked)
        total_cells = sum(
            t.get("complexity", {}).get("rows", 0) * t.get("complexity", {}).get("cols", 0)
            for t in self.tables_checked
        )

        uncertain_ratio = total_uncertain / total_cells if total_cells > 0 else 0
        coverage = (1 - uncertain_ratio * 0.5) * 100  # Assume each uncertain cell affects 50%

        return {
            "total_tables": self.total_tables,
            "manual_check_tables": manual_check_count,
            "manual_check_ratio": manual_check_count / self.total_tables if self.total_tables > 0 else 0,
            "avg_confidence": avg_confidence,
            "coverage": coverage
        }
