"""文本提取器"""

from typing import List, Any
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class TextExtractor:
    """文本提取器"""

    def __init__(self):
        self.logger = logger

    def extract(self, page: Any, exclude_regions: List[tuple] = None) -> str:
        """
        提取文本

        Args:
            page: pdfplumber页面对象
            exclude_regions: 排除区域列表 [(x0, y0, x1, y1), ...]

        Returns:
            提取的文本
        """
        try:
            # 简化实现：直接使用page.extract_text()
            text = page.extract_text()

            if text:
                # 清理文本
                text = self._clean_text(text)

            return text or ""

        except Exception as e:
            self.logger.error(f"文本提取失败: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除过多的空白行
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)

        return "\n".join(cleaned_lines)
