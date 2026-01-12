"""主编排器 - 协调所有模块完成PDF到Markdown的转换"""

import os
from typing import Optional
from datasheet_to_markdown.core.parser import PDFParser
from datasheet_to_markdown.core.classifier import ContentBlockClassifier, ContentType
from datasheet_to_markdown.extractors.table import TableExtractor
from datasheet_to_markdown.extractors.image import ImageExtractor
from datasheet_to_markdown.builder import DocumentBuilder
from datasheet_to_markdown.quality.reporter import QualityReporter
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatasheetConverter:
    """Datasheet转换器 - 主编排器"""

    def __init__(self, pdf_path: str, output_dir: str = None,
                 add_toc: bool = False, confidence_threshold: float = 50,
                 verbose: bool = False):
        """
        初始化转换器

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            add_toc: 是否添加目录
            confidence_threshold: 置信度阈值（0-100）
            verbose: 是否详细输出
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir or "./output"
        self.add_toc = add_toc
        self.confidence_threshold = confidence_threshold
        self.verbose = verbose

        # 设置日志级别
        if verbose:
            logger.setLevel(10)  # DEBUG

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        self.images_dir = os.path.join(self.output_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)

        # 初始化组件
        self.pdf_parser: Optional[PDFParser] = None
        self.document_builder: Optional[DocumentBuilder] = None
        self.quality_reporter = QualityReporter()

        self.logger = logger

    def convert(self) -> str:
        """
        执行转换

        Returns:
            输出文件路径
        """
        try:
            # 1. 打开PDF
            self.logger.info(f"📄 正在转换: {self.pdf_path}")
            self.pdf_parser = PDFParser(self.pdf_path)
            self.pdf_parser.open()

            page_count = self.pdf_parser.page_count
            self.logger.info(f"📊 总页数: {page_count}")

            # 2. 初始化文档构建器
            doc_title = os.path.splitext(os.path.basename(self.pdf_path))[0]
            self.document_builder = DocumentBuilder(
                title=doc_title,
                add_toc=self.add_toc
            )

            # 3. 逐页处理
            for page_num in range(page_count):
                self._process_page(page_num)

            # 4. 构建Markdown文档
            markdown = self.document_builder.build()

            # 5. 保存文档
            output_file = os.path.join(self.output_dir, "datasheet.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)

            self.logger.info(f"✓ Markdown生成完成")
            self.logger.info(f"📄 输出文件: {output_file}")

            # 6. 输出质量报告
            self.quality_reporter.print_summary()

            return output_file

        except Exception as e:
            self.logger.error(f"转换失败: {e}")
            raise
        finally:
            # 关闭PDF
            if self.pdf_parser:
                self.pdf_parser.close()

    def _process_page(self, page_num: int):
        """
        处理单个页面

        Args:
            page_num: 页码（从0开始）
        """
        if self.verbose:
            self.logger.info(f"正在处理页面: {page_num + 1}/{self.pdf_parser.page_count}")

        # 获取页面
        page = self.pdf_parser.get_page(page_num)
        if not page:
            self.logger.warning(f"页面 {page_num + 1} 不存在")
            return

        page_height = page.height

        # 内容块分类
        classifier = ContentBlockClassifier(page, page_num + 1, page_height)
        content_blocks = classifier.classify()

        # 提取表格（使用pdfplumber）
        table_extractor = TableExtractor(
            self.pdf_path,
            page_num + 1,
            self.confidence_threshold
        )
        tables = table_extractor.extract(page)

        # 提取图片
        image_extractor = ImageExtractor(self.images_dir)
        images = image_extractor.extract(page, page_num + 1)

        # 合并内容块并按类型处理
        self._process_content_blocks(content_blocks, tables, images, page_num + 1)

    def _process_content_blocks(self, content_blocks, tables, images, page_num: int):
        """
        处理内容块并添加到文档

        Args:
            content_blocks: 内容块列表
            tables: 表格列表
            images: 图片列表
            page_num: 页码
        """
        # 简化处理：按顺序处理内容块
        for block in content_blocks:
            if block.type == ContentType.HEADING:
                # 添加标题
                level = block.heading_level or 2
                self.document_builder.add_heading(block.content, level)

            elif block.type == ContentType.PARAGRAPH:
                # 添加段落
                self.document_builder.add_paragraph(block.content)

            elif block.type == ContentType.LIST:
                # 添加列表
                self.document_builder.add_list(
                    block.list_items,
                    block.list_ordered
                )

        # 添加表格
        for table in tables:
            self.document_builder.add_table(
                table["data"],
                caption=f"Table {page_num}-{table['index']}",
                manual_check=table["needs_manual_check"],
                uncertain_cells=table["uncertain_cells"]
            )

            # 记录质量信息
            self.quality_reporter.report_table({
                "page_num": page_num,
                "caption": f"Table {page_num}-{table['index']}",
                "flask": table["flask"],
                "needs_manual_check": table["needs_manual_check"],
                "complexity": table["complexity"],
                "uncertain_cells": table["uncertain_cells"]
            })

        # 添加图片引用
        for img in images:
            self.document_builder.add_image(
                img["path"],
                alt=f"Image on page {page_num}"
            )
