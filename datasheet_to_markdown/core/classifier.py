"""内容块分类器 - 核心模块

负责将PDF页面内容分类为不同的内容块:
- 标题 (HEADING)
- 段落 (PARAGRAPH)
- 列表 (LIST)
- 表格 (TABLE)
- 图片 (IMAGE)
- 页眉页脚 (FOOTER) - 需要过滤
- 页码 (PAGE_NUMBER) - 需要过滤
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Dict
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentType(Enum):
    """内容类型枚举"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    FOOTER = "footer"
    PAGE_NUMBER = "page_number"


@dataclass
class ContentBlock:
    """内容块数据结构"""
    type: ContentType
    content: Any
    page_num: int
    bbox: tuple  # (x0, y0, x1, y1)
    metadata: Dict = field(default_factory=dict)

    # 标题特有属性
    heading_level: Optional[int] = None

    # 列表特有属性
    list_ordered: bool = False
    list_items: List[str] = field(default_factory=list)

    # 表格特有属性
    table_shape: Optional[tuple] = None  # (rows, cols)
    table_flask: Optional[float] = None  # camelot准确率评分

    # 图片特有属性
    image_path: Optional[str] = None

    # 置信度相关
    needs_manual_check: bool = False
    uncertain_cells: List[tuple] = field(default_factory=list)


class ContentBlockClassifier:
    """内容块分类器 - 核心类"""

    # 章节号正则模式（按优先级排序）
    SECTION_PATTERNS = [
        (r'^(\d+)\.(\d+)\.(\d+)\s+(.+)$', 3),  # "3.1.2 Subsection" → Level 3
        (r'^(\d+)\.(\d+)\.\s+(.+)$', 2),      # "2.1 Description" → Level 2
        (r'^(\d+)\.\s+(.+)$', 1),             # "1. Features" → Level 1
        (r'^([A-Z][A-Z\s\d]+)$', 2),          # "FEATURES" → Level 2
    ]

    def __init__(self, page: Any, page_num: int, page_height: float):
        """
        初始化分类器

        Args:
            page: pdfplumber页面对象
            page_num: 页码
            page_height: 页面高度
        """
        self.page = page
        self.page_num = page_num
        self.page_height = page_height
        self.logger = logger

    def classify(self) -> List[ContentBlock]:
        """
        分类页面内容为多个内容块

        Returns:
            ContentBlock列表，按页面从上到下排序
        """
        blocks = []

        # 1. 提取文本块
        text_blocks = self._extract_text_blocks()
        blocks.extend(text_blocks)

        # 2. 提取图片（使用pdfplumber）
        images = self._extract_images()
        blocks.extend(images)

        # 3. 按位置排序（从上到下，y坐标从大到小）
        blocks.sort(key=lambda b: b.bbox[1], reverse=True)

        # 4. 过滤页眉页脚和页码
        blocks = [b for b in blocks if not self._is_footer(b)]

        self.logger.debug(f"页面 {self.page_num}: 分类出 {len(blocks)} 个内容块")

        return blocks

    def _extract_text_blocks(self) -> List[ContentBlock]:
        """提取文本块"""
        blocks = []
        words = self.page.extract_words()

        if not words:
            return blocks

        # 按位置分组单词为文本行
        lines = self._group_words_to_lines(words)

        for line_words in lines:
            if not line_words:
                continue

            # 合并为文本
            text = " ".join([w["text"] for w in line_words])
            text = text.strip()

            if not text:
                continue

            # 计算边界框
            x0 = min(w["x0"] for w in line_words)
            y0 = min(w["top"] for w in line_words)
            x1 = max(w["x1"] for w in line_words)
            y1 = max(w["bottom"] for w in line_words)

            # 判断内容类型
            content_type, metadata = self._classify_text_type(text, line_words)

            # 创建内容块
            if content_type == ContentType.HEADING:
                level = self._extract_heading_level(text)
                block = ContentBlock(
                    type=content_type,
                    content=text,
                    page_num=self.page_num,
                    bbox=(x0, y0, x1, y1),
                    metadata=metadata,
                    heading_level=level
                )
            elif content_type == ContentType.LIST:
                block = ContentBlock(
                    type=content_type,
                    content=text,
                    page_num=self.page_num,
                    bbox=(x0, y0, x1, y1),
                    metadata=metadata,
                    list_ordered=metadata.get("ordered", False),
                    list_items=[text]
                )
            else:  # PARAGRAPH
                block = ContentBlock(
                    type=content_type,
                    content=text,
                    page_num=self.page_num,
                    bbox=(x0, y0, x1, y1),
                    metadata=metadata
                )

            blocks.append(block)

        return blocks

    def _group_words_to_lines(self, words: List[Dict]) -> List[List[Dict]]:
        """将单词按行分组"""
        if not words:
            return []

        # 按y坐标排序
        words_sorted = sorted(words, key=lambda w: w["top"])

        lines = []
        current_line = [words_sorted[0]]
        current_y = words_sorted[0]["top"]
        y_threshold = 5  # y坐标容差

        for word in words_sorted[1:]:
            if abs(word["top"] - current_y) <= y_threshold:
                current_line.append(word)
            else:
                # 按x坐标排序当前行
                lines.append(sorted(current_line, key=lambda w: w["x0"]))
                current_line = [word]
                current_y = word["top"]

        # 添加最后一行
        if current_line:
            lines.append(sorted(current_line, key=lambda w: w["x0"]))

        return lines

    def _classify_text_type(self, text: str, words: List[Dict]) -> tuple:
        """
        分类文本类型

        Returns:
            (ContentType, metadata)
        """
        # 检查是否为标题
        if self._is_heading(text, words):
            return ContentType.HEADING, {"confidence": 0.95}

        # 检查是否为列表
        if self._is_list(text):
            ordered = text[0].isdigit()
            return ContentType.LIST, {"ordered": ordered}

        # 默认为段落
        return ContentType.PARAGRAPH, {}

    def _is_heading(self, text: str, words: List[Dict]) -> bool:
        """
        判断是否为标题

        规则：
        1. 正则匹配章节号（优先）
        2. 字体大小大于普通文本（备选）
        """
        # 规则1: 正则匹配
        for pattern, _ in self.SECTION_PATTERNS:
            if re.match(pattern, text.strip()):
                return True

        # 规则2: 字体大小（如果有字体信息）
        if words and "size" in words[0]:
            avg_font_size = sum(w.get("size", 12) for w in words) / len(words)
            if avg_font_size > 14:  # 假设普通文本字体≤14
                return True

        return False

    def _is_list(self, text: str) -> bool:
        """
        判断是否为列表

        规则：
        - 以"•", "-", "*"开头 → 无序列表
        - 以数字+点开头 → 有序列表
        """
        stripped = text.strip()

        # 无序列表标记
        unordered_markers = ["•", "-", "*", "·"]
        if stripped[0] in unordered_markers if stripped else False:
            return True

        # 有序列表（数字开头）
        if re.match(r'^\d+[\.\)]\s+', stripped):
            return True

        return False

    def _is_footer(self, block: ContentBlock) -> bool:
        """
        判断是否为页眉页脚

        规则：
        - 出现在页面顶部或底部10%区域
        - 包含页码、公司名称、文档标题等
        """
        y0 = block.bbox[1]

        # 位置规则：顶部10%或底部10%
        if y0 > self.page_height * 0.9 or y0 < self.page_height * 0.1:
            # 内容规则
            text = str(block.content).strip()

            # 纯数字（页码）
            if re.match(r'^\s*\d+\s*$', text):
                return True

            # 包含"Page"或"页"
            if re.match(r'.*(page|页)\s*\d+.*', text, re.I):
                return True

            # "- X -" 格式页码
            if re.match(r'^\s*-\s*\d+\s*-\s*$', text):
                return True

            # 全大写短文本（可能是公司名称，重复出现）
            if len(text) < 50 and text.isupper() and not block.type == ContentType.HEADING:
                # 这里的简化处理：如果不是标题的全大写短文本，可能是页眉
                return True

        return False

    def _extract_heading_level(self, text: str) -> int:
        """
        提取标题层级

        规则：
        - "1. Features" → 1级标题（#）
        - "2.1 Description" → 2级标题（##）
        - "3.1.2 Pin Functions" → 3级标题（###）
        """
        for pattern, level in self.SECTION_PATTERNS:
            match = re.match(pattern, text.strip())
            if match:
                return level

        # 默认2级
        return 2

    def _extract_images(self) -> List[ContentBlock]:
        """
        提取图片（简化版，实际图片提取在ImageExtractor中）
        """
        # 简化实现：检测页面中的图片区域
        images = []

        # pdfplumber的images检测
        if hasattr(self.page, "images"):
            for img in self.page.images:
                # 图片边界框
                bbox = (
                    img.get("x0", 0),
                    img.get("y0", 0),
                    img.get("x1", 0),
                    img.get("y1", 0)
                )

                block = ContentBlock(
                    type=ContentType.IMAGE,
                    content=img,
                    page_num=self.page_num,
                    bbox=bbox,
                    metadata={"image_type": img.get("stream_type", "unknown")}
                )

                images.append(block)

        return images
