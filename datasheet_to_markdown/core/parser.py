"""PDF解析器 - 负责加载和提供PDF基础信息"""

import pdfplumber
from typing import Optional, Any
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser:
    """PDF解析器"""

    def __init__(self, pdf_path: str):
        """
        初始化PDF解析器

        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = pdf_path
        self.pdf: Optional[Any] = None
        self.logger = logger

    def open(self) -> None:
        """打开PDF文件"""
        try:
            self.pdf = pdfplumber.open(self.pdf_path)
            self.logger.info(f"成功打开PDF: {self.pdf_path}")
            self.logger.info(f"总页数: {self.page_count}")
        except Exception as e:
            self.logger.error(f"打开PDF失败: {e}")
            raise

    def close(self) -> None:
        """关闭PDF文件"""
        if self.pdf:
            self.pdf.close()
            self.logger.info("PDF文件已关闭")

    @property
    def page_count(self) -> int:
        """获取PDF总页数"""
        if self.pdf:
            return len(self.pdf.pages)
        return 0

    def get_page(self, page_num: int) -> Optional[Any]:
        """
        获取指定页

        Args:
            page_num: 页码（从0开始）

        Returns:
            pdfplumber.Page对象
        """
        if self.pdf and 0 <= page_num < self.page_count:
            return self.pdf.pages[page_num]
        return None

    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
