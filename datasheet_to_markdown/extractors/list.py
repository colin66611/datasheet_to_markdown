"""列表提取器"""

from typing import List, Dict
import re
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ListExtractor:
    """列表提取器"""

    def __init__(self):
        self.logger = logger

    def extract(self, text_blocks: List[str]) -> List[Dict]:
        """
        提取列表

        Args:
            text_blocks: 文本块列表

        Returns:
            列表项列表：
            [
                {
                    "type": "ordered" or "unordered",
                    "items": ["Item 1", "Item 2", ...],
                    "indent": 0  # 缩进级别
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
                    # 开始新列表
                    if current_list:
                        result.append(current_list)

                    current_list = {
                        "type": list_type,
                        "items": [],
                        "indent": 0
                    }

                # 添加到当前列表
                current_list["items"].append(text.strip())

            else:
                # 非列表项，结束当前列表
                if current_list:
                    result.append(current_list)
                    current_list = None

        # 添加最后一个列表
        if current_list:
            result.append(current_list)

        return result

    def _is_list_item(self, text: str) -> bool:
        """
        判断是否为列表项

        Args:
            text: 文本内容

        Returns:
            True表示是列表项
        """
        stripped = text.strip()

        # 无序列表标记
        unordered_markers = ["•", "-", "*", "·"]
        if stripped and stripped[0] in unordered_markers:
            return True

        # 有序列表（数字开头）
        if re.match(r'^\d+[\.\)]\s+', stripped):
            return True

        return False

    def _get_list_type(self, text: str) -> str:
        """
        获取列表类型

        Args:
            text: 文本内容

        Returns:
            "ordered" 或 "unordered"
        """
        stripped = text.strip()

        # 检查是否为有序列表
        if re.match(r'^\d+[\.\)]\s+', stripped):
            return "ordered"

        return "unordered"
