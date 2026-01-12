"""文档构建器 - 组装完整的Markdown文档"""

from typing import List, Optional
from .converters.markdown import MarkdownConverter
from .converters.marker import ManualMarker
from .core.classifier import ContentBlock, ContentType
from .utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentBuilder:
    """文档构建器"""

    def __init__(self, title: str = None, add_toc: bool = False):
        """
        初始化文档构建器

        Args:
            title: 文档标题
            add_toc: 是否添加目录
        """
        self.title = title or "Document"
        self.add_toc = add_toc
        self.converter = MarkdownConverter()
        self.marker = ManualMarker()
        self.content_parts = []
        self.headings = []
        self.logger = logger

    def add_heading(self, text: str, level: int):
        """
        添加标题

        Args:
            text: 标题文本
            level: 层级（1-6）
        """
        markdown = self.converter.heading_to_markdown(text, level)
        self.content_parts.append(markdown)

        # 记录标题用于生成目录
        self.headings.append({
            "level": level,
            "text": text
        })

        self.logger.debug(f"添加标题: {'#' * level} {text}")

    def add_paragraph(self, text: str):
        """添加段落"""
        markdown = self.converter.paragraph_to_markdown(text)
        self.content_parts.append(markdown)
        self.logger.debug(f"添加段落: {text[:50]}...")

    def add_list(self, items: List[str], ordered: bool = False):
        """
        添加列表

        Args:
            items: 列表项
            ordered: 是否有序列表
        """
        markdown = self.converter.list_to_markdown(items, ordered)
        self.content_parts.append(markdown)
        self.logger.debug(f"添加列表: {len(items)} 项")

    def add_table(self, table_data: List[List[str]],
                  caption: str = None,
                  manual_check: bool = False,
                  uncertain_cells: List[tuple] = None):
        """
        添加表格

        Args:
            table_data: 表格数据
            caption: 表格标题
            manual_check: 是否标记为需要人工核对
            uncertain_cells: 可疑单元格坐标
        """
        markdown = self.converter.table_to_markdown(
            table_data, caption, manual_check, uncertain_cells
        )
        self.content_parts.append(markdown)
        self.logger.debug(
            f"添加表格: {len(table_data)}行×{len(table_data[0]) if table_data else 0}列, "
            f"人工核对={'是' if manual_check else '否'}"
        )

    def add_image(self, path: str, alt: str = None):
        """
        添加图片引用

        Args:
            path: 图片路径
            alt: 替代文本
        """
        markdown = self.converter.image_to_markdown(path, alt)
        self.content_parts.append(markdown)
        self.logger.debug(f"添加图片: {path}")

    def add_raw(self, text: str):
        """添加原始文本"""
        self.content_parts.append(text)

    def add_toc(self):
        """添加目录"""
        if not self.headings:
            return

        toc_lines = ["## Table of Contents\n\n"]

        for heading in self.headings:
            # 生成锚点
            anchor = heading["text"].lower().replace(" ", "-").replace(".", "")
            # 根据层级缩进
            indent = "  " * (heading["level"] - 1)
            toc_lines.append(f"{indent}- [{heading['text']}](#{anchor})")

        toc_lines.append("\n")
        self.content_parts.insert(0, "\n".join(toc_lines))
        self.logger.debug(f"添加目录: {len(self.headings)} 个标题")

    def build(self) -> str:
        """
        构建完整的Markdown文档

        Returns:
            Markdown字符串
        """
        # 添加文档标题
        document = f"# {self.title}\n\n"

        # 添加目录（如果需要）
        if self.add_toc and self.headings:
            toc_parts = self._build_toc()
            document += toc_parts + "\n"

        # 添加所有内容
        document += "".join(self.content_parts)

        return document

    def _build_toc(self) -> str:
        """构建目录"""
        toc_lines = ["## Table of Contents\n\n"]

        for heading in self.headings:
            # 生成锚点
            anchor = heading["text"].lower().replace(" ", "-").replace(".", "")
            # 根据层级缩进
            indent = "  " * (heading["level"] - 1)
            toc_lines.append(f"{indent}- [{heading['text']}](#{anchor})")

        toc_lines.append("\n" + self.converter.horizontal_rule())

        return "\n".join(toc_lines)

    def get_stats(self) -> dict:
        """获取文档统计信息"""
        stats = {
            "total_headings": len(self.headings),
            "headings_by_level": {},
            "total_parts": len(self.content_parts)
        }

        for heading in self.headings:
            level = heading["level"]
            stats["headings_by_level"][level] = \
                stats["headings_by_level"].get(level, 0) + 1

        return stats
