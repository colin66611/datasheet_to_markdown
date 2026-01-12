"""Main orchestrator - Coordinates all modules to complete PDF to Markdown conversion"""

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
    """Datasheet Converter - Main orchestrator"""

    def __init__(self, pdf_path: str, output_dir: str = None,
                 add_toc: bool = False, confidence_threshold: float = 50,
                 verbose: bool = False):
        """
        Initialize converter

        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory
            add_toc: Whether to add table of contents
            confidence_threshold: Confidence threshold (0-100)
            verbose: Whether to enable verbose output
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir or "./output"
        self.add_toc = add_toc
        self.confidence_threshold = confidence_threshold
        self.verbose = verbose

        # Set log level
        if verbose:
            logger.setLevel(10)  # DEBUG

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        self.images_dir = os.path.join(self.output_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)

        # Initialize components
        self.pdf_parser: Optional[PDFParser] = None
        self.document_builder: Optional[DocumentBuilder] = None
        self.quality_reporter = QualityReporter()

        self.logger = logger

    def convert(self) -> str:
        """
        Execute conversion

        Returns:
            Output file path
        """
        try:
            # 1. Open PDF
            self.logger.info(f"📄 Converting: {self.pdf_path}")
            self.pdf_parser = PDFParser(self.pdf_path)
            self.pdf_parser.open()

            page_count = self.pdf_parser.page_count
            self.logger.info(f"📊 Total pages: {page_count}")

            # 2. Initialize document builder
            doc_title = os.path.splitext(os.path.basename(self.pdf_path))[0]
            self.document_builder = DocumentBuilder(
                title=doc_title,
                add_toc=self.add_toc
            )

            # 3. Process pages one by one
            for page_num in range(page_count):
                self._process_page(page_num)

            # 4. Build Markdown document
            markdown = self.document_builder.build()

            # 5. Save document
            output_file = os.path.join(self.output_dir, "datasheet.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)

            self.logger.info(f"✓ Markdown generation complete")
            self.logger.info(f"📄 Output file: {output_file}")

            # 6. Output quality report
            self.quality_reporter.print_summary()

            return output_file

        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            raise
        finally:
            # Close PDF
            if self.pdf_parser:
                self.pdf_parser.close()

    def _process_page(self, page_num: int):
        """
        Process single page

        Args:
            page_num: Page number (starting from 0)
        """
        if self.verbose:
            self.logger.info(f"Processing page: {page_num + 1}/{self.pdf_parser.page_count}")

        # Get page
        page = self.pdf_parser.get_page(page_num)
        if not page:
            self.logger.warning(f"Page {page_num + 1} does not exist")
            return

        page_height = page.height

        # Content block classification
        classifier = ContentBlockClassifier(page, page_num + 1, page_height)
        content_blocks = classifier.classify()

        # Extract tables (using pdfplumber)
        table_extractor = TableExtractor(
            self.pdf_path,
            page_num + 1,
            self.confidence_threshold
        )
        tables = table_extractor.extract(page)

        # Extract images
        image_extractor = ImageExtractor(self.images_dir)
        images = image_extractor.extract(page, page_num + 1)

        # Merge content blocks and process by type
        self._process_content_blocks(content_blocks, tables, images, page_num + 1)

    def _process_content_blocks(self, content_blocks, tables, images, page_num: int):
        """
        Process content blocks and add to document

        Args:
            content_blocks: List of content blocks
            tables: List of tables
            images: List of images
            page_num: Page number
        """
        # Simplified processing: process content blocks in order
        for block in content_blocks:
            if block.type == ContentType.HEADING:
                # Add heading
                level = block.heading_level or 2
                self.document_builder.add_heading(block.content, level)

            elif block.type == ContentType.PARAGRAPH:
                # Add paragraph
                self.document_builder.add_paragraph(block.content)

            elif block.type == ContentType.LIST:
                # Add list
                self.document_builder.add_list(
                    block.list_items,
                    block.list_ordered
                )

        # Add tables
        for table in tables:
            self.document_builder.add_table(
                table["data"],
                caption=f"Table {page_num}-{table['index']}",
                manual_check=table["needs_manual_check"],
                uncertain_cells=table["uncertain_cells"]
            )

            # Record quality information
            self.quality_reporter.report_table({
                "page_num": page_num,
                "caption": f"Table {page_num}-{table['index']}",
                "flask": table["flask"],
                "needs_manual_check": table["needs_manual_check"],
                "complexity": table["complexity"],
                "uncertain_cells": table["uncertain_cells"]
            })

        # Add image references
        for img in images:
            self.document_builder.add_image(
                img["path"],
                alt=f"Image on page {page_num}"
            )
