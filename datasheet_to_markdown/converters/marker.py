"""人工介入标记器"""

from typing import List, Tuple
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ManualMarker:
    """人工介入标记器"""

    def __init__(self):
        self.logger = logger

    def mark_table(self, table_data: List[List[str]],
                  uncertain_cells: List[Tuple[int, int]]) -> List[List[str]]:
        """
        标记表格中需要人工核对的内容

        规则：
        - 单元格级：在可疑单元格内容后添加 [UNCERTAIN]

        Args:
            table_data: 表格数据
            uncertain_cells: 可疑单元格坐标列表

        Returns:
            标记后的表格数据
        """
        if not uncertain_cells:
            return table_data

        marked_table = []

        for row_idx, row in enumerate(table_data):
            marked_row = []
            for col_idx, cell in enumerate(row):
                cell_str = str(cell) if cell is not None else ""

                # 检查是否为可疑单元格
                if (row_idx, col_idx) in uncertain_cells:
                    cell_str = f"{cell_str} [UNCERTAIN]"

                marked_row.append(cell_str)

            marked_table.append(marked_row)

        self.logger.debug(f"标记了 {len(uncertain_cells)} 个可疑单元格")
        return marked_table

    def mark_text(self, text: str, issues: List[str]) -> str:
        """
        标记文本中需要人工核对的内容

        Args:
            text: 文本内容
            issues: 问题列表

        Returns:
            标记后的文本
        """
        if not issues:
            return text

        # 在文本后添加警告标记
        marked = f"{text}\n\n<!-- Issues: {', '.join(issues)} -->"

        return marked

    def add_table_marker(self, markdown: str, needs_check: bool) -> str:
        """
        在表格标题后添加人工核对标记

        Args:
            markdown: 原始markdown文本
            needs_check: 是否需要人工核对

        Returns:
            添加标记后的markdown
        """
        if needs_check:
            # 在表格标题或说明后添加 [MANUAL_CHECK]
            if markdown.strip().startswith("|"):
                # 如果直接是表格，在前面添加注释
                return f"<!-- [MANUAL_CHECK] This table requires manual verification -->\n\n{markdown}"
            else:
                # 如果有标题，在标题后添加标记
                return f"{markdown} [MANUAL_CHECK]"

        return markdown
