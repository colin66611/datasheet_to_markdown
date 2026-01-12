"""置信度分析器 - 对提取的内容进行置信度评分"""

from typing import List, Tuple, Dict
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConfidenceScorer:
    """置信度分析器"""

    def __init__(self, threshold: float = 50):
        """
        初始化置信度分析器

        Args:
            threshold: 可疑度阈值（0-100），超过此值标记为可疑
        """
        self.threshold = threshold
        self.logger = logger

    def score_table(self, table_data: List[List[str]], flask: float) -> Dict:
        """
        对表格进行置信度评分

        Args:
            table_data: 表格数据
            flask: camelot的准确率评分

        Returns:
            评分结果：
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

        # 逐个评分单元格
        for row_idx, row in enumerate(table_data):
            row_scores = []
            for col_idx, cell in enumerate(row):
                score = self._score_cell(cell)
                row_scores.append(score)

                if score < self.threshold:
                    uncertain_cells.append((row_idx, col_idx))
                    issues.append(f"Low confidence ({score:.1f}) at ({row_idx},{col_idx})")

            cell_confidence.append(row_scores)

        # 计算总体置信度
        flat_scores = [score for row in cell_confidence for score in row]
        overall = sum(flat_scores) / len(flat_scores) if flat_scores else 0.0

        # 结合camelot的flask评分
        overall = (overall + flask) / 2

        self.logger.debug(f"表格置信度: {overall:.2f}, 可疑单元格: {len(uncertain_cells)}")

        return {
            "overall_confidence": overall,
            "cell_confidence": cell_confidence,
            "uncertain_cells": uncertain_cells,
            "issues": issues
        }

    def _score_cell(self, cell: str) -> float:
        """
        单元格评分

        规则：
        - 空单元格：0分
        - 截断文本：20分
        - 正常文本：100分
        """
        if not cell or str(cell).strip() == "":
            return 0.0

        cell_str = str(cell)

        if self._is_truncated(cell_str):
            return 20.0

        return 100.0

    def _is_truncated(self, text: str) -> bool:
        """
        检测截断文本

        规则：
        - 包含"..."
        - 以"<"或">"结尾
        - 包含"(continued)"
        """
        indicators = ["...", "(continued)", "(Continued)"]

        for ind in indicators:
            if ind in text:
                return True

        # 以<或>结尾
        if text.endswith("<") or text.endswith(">"):
            return True

        return False

    def analyze_table_complexity(self, table_data: List[List[str]]) -> Dict:
        """
        分析表格复杂度

        Args:
            table_data: 表格数据

        Returns:
            复杂度分析：
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

        # 检查空单元格
        empty_count = 0
        total_cells = rows * cols

        for row in table_data:
            for cell in row:
                if not cell or str(cell).strip() == "":
                    empty_count += 1

        has_empty = empty_count > 0

        # 复杂度评分（0-1）
        # 大表格、多空单元格会增加复杂度
        size_complexity = min((rows * cols) / 200, 1.0)  # 最多200个单元格
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
        判断是否需要人工核对

        触发条件（满足任一）：
        - 行数 > 20 或 列数 > 6
        - flask < 80
        - 可疑单元格比例 > 50%

        Args:
            complexity: 复杂度分析
            flask: 准确率评分
            uncertain_ratio: 可疑单元格比例

        Returns:
            True表示需要人工核对
        """
        # 条件1: 表格尺寸过大
        if complexity.get("rows", 0) > 20 or complexity.get("cols", 0) > 6:
            return True

        # 条件2: 准确率低
        if flask < 80:
            return True

        # 条件3: 可疑单元格比例高
        if uncertain_ratio > 0.5:
            return True

        return False
