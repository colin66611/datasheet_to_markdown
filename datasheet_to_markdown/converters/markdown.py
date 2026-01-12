"""Markdown转换器 - 将各种内容转换为Markdown格式"""

from typing import List, Optional, Tuple
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class MarkdownConverter:
    """Markdown转换器"""

    def __init__(self):
        self.logger = logger

    def heading_to_markdown(self, text: str, level: int) -> str:
        """
        标题转Markdown

        Args:
            text: 标题文本
            level: 层级（1-6）

        Returns:
            Markdown格式标题
        """
        if level < 1 or level > 6:
            level = 2

        prefix = "#" * level
        return f"{prefix} {text}\n\n"

    def paragraph_to_markdown(self, text: str) -> str:
        """
        段落转Markdown

        Args:
            text: 段落文本

        Returns:
            Markdown格式段落
        """
        if not text:
            return ""

        # 清理文本
        cleaned = text.strip()

        return f"{cleaned}\n\n"

    def list_to_markdown(self, items: List[str], ordered: bool = False) -> str:
        """
        列表转Markdown

        Args:
            items: 列表项
            ordered: 是否有序列表

        Returns:
            Markdown格式列表
        """
        if not items:
            return ""

        lines = []
        for i, item in enumerate(items):
            if ordered:
                # 有序列表：1. Item
                prefix = f"{i + 1}."
            else:
                # 无序列表：- Item
                prefix = "-"

            # 清理列表项标记（如果已有）
            cleaned_item = item.strip()
            # 移除开头的 •, -, *, · 等
            for marker in ["•", "-", "*", "·"]:
                if cleaned_item.startswith(marker):
                    cleaned_item = cleaned_item[1:].strip()
                    break

            # 移除开头的数字+点（如果是有序列表）
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
        表格转Markdown

        Args:
            table_data: 表格数据（二维列表）
            caption: 表格标题
            manual_check: 是否需要人工核对
            uncertain_cells: 可疑单元格坐标

        Returns:
            Markdown格式表格
        """
        if not table_data or not table_data[0]:
            return ""

        # 标记可疑单元格
        if uncertain_cells:
            cell_set = set(uncertain_cells)
            for row_idx, row in enumerate(table_data):
                for col_idx in range(len(row)):
                    if (row_idx, col_idx) in cell_set:
                        table_data[row_idx][col_idx] = f"{table_data[row_idx][col_idx]} [UNCERTAIN]"

        # 生成Markdown表格
        lines = []

        # 表头
        header = table_data[0]
        lines.append("| " + " | ".join(str(cell) for cell in header) + " |")

        # 分隔线
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")

        # 数据行
        for row in table_data[1:]:
            # 确保每行列数一致
            while len(row) < len(header):
                row.append("")
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        result = "\n".join(lines) + "\n\n"

        # 添加标题
        if caption:
            caption_prefix = ""
            if manual_check:
                caption_prefix = " [MANUAL_CHECK]"

            result = f"### {caption}{caption_prefix}\n\n{result}"

        return result

    def image_to_markdown(self, image_path: str, alt: Optional[str] = None) -> str:
        """
        图片转Markdown

        Args:
            image_path: 图片路径
            alt: 替代文本

        Returns:
            Markdown格式图片
        """
        if not alt:
            alt = "Image"

        return f"![{alt}]({image_path})\n\n"

    def code_to_markdown(self, code: str, language: str = "") -> str:
        """
        代码块转Markdown

        Args:
            code: 代码内容
            language: 语言标识

        Returns:
            Markdown格式代码块
        """
        return f"```{language}\n{code}\n```\n\n"

    def horizontal_rule(self) -> str:
        """生成分隔线"""
        return "---\n\n"
