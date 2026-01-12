"""标题识别器 - 专门负责标题识别和层级提取"""

import re
from typing import Optional, Dict
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class HeadingDetector:
    """标题识别器"""

    # 章节号正则模式
    SECTION_PATTERNS = [
        r'^(\d+)\.\s+(.+)$',           # "1. Features"
        r'^(\d+)\.(\d+)\.\s+(.+)$',    # "2.1 Description"
        r'^(\d+)\.(\d+)\.(\d+)\s+(.+)$',  # "3.1.2 Subsection"
        r'^([A-Z][A-Z\s\d]+)$',        # "FEATURES", "PIN CONFIGURATION"
    ]

    def __init__(self):
        self.logger = logger

    def detect(self, text: str, font_size: float = None) -> Optional[Dict]:
        """
        检测文本是否为标题

        Args:
            text: 文本内容
            font_size: 字体大小（可选）

        Returns:
            如果是标题，返回：
            {
                "level": 1-6,
                "text": "标题文本",
                "confidence": 0.0-1.0
            }
            否则返回None
        """
        # 优先使用正则匹配
        for pattern in self.SECTION_PATTERNS:
            match = re.match(pattern, text.strip())
            if match:
                level = self._extract_level_from_pattern(pattern, match)
                return {
                    "level": level,
                    "text": text.strip(),
                    "confidence": 0.95
                }

        # 备选：根据字体大小判断
        if font_size and font_size > 14:  # 假设普通文本字体≤14
            return {
                "level": self._estimate_level_from_font(font_size),
                "text": text.strip(),
                "confidence": 0.7
            }

        return None

    def extract_level(self, text: str) -> int:
        """
        从标题文本中提取层级

        Args:
            text: 标题文本

        Returns:
            层级（1-6）
        """
        for pattern in self.SECTION_PATTERNS:
            match = re.match(pattern, text.strip())
            if match:
                return self._extract_level_from_pattern(pattern, match)

        # 默认2级
        return 2

    def _extract_level_from_pattern(self, pattern: str, match: re.Match) -> int:
        """从正则匹配结果中提取层级"""
        # "1. Features" → Level 1
        if r'^(\d+)\.\s+' in pattern:
            return 1

        # "2.1 Description" → Level 2
        if r'^(\d+)\.(\d+)\.\s+' in pattern:
            return 2

        # "3.1.2 Subsection" → Level 3
        if r'^(\d+)\.(\d+)\.(\d+)\s+' in pattern:
            return 3

        # 全大写标题 → Level 2
        if r'^([A-Z][A-Z\s\d]+)$' in pattern:
            return 2

        return 2

    def _estimate_level_from_font(self, font_size: float) -> int:
        """根据字体大小估算层级"""
        if font_size >= 20:
            return 1
        elif font_size >= 16:
            return 2
        elif font_size >= 14:
            return 3
        else:
            return 4
