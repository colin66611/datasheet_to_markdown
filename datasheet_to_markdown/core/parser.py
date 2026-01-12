"""PDF Parser - Responsible for loading and providing basic PDF information"""

import pdfplumber
from typing import Optional, Any
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser:
    """PDF Parser"""

    def __init__(self, pdf_path: str):
        """
        Initialize PDF parser

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = pdf_path
        self.pdf: Optional[Any] = None
        self.logger = logger

    def open(self) -> None:
        """Open PDF file"""
        try:
            self.pdf = pdfplumber.open(self.pdf_path)
            self.logger.info(f"Successfully opened PDF: {self.pdf_path}")
            self.logger.info(f"Total pages: {self.page_count}")
        except Exception as e:
            self.logger.error(f"Failed to open PDF: {e}")
            raise

    def close(self) -> None:
        """Close PDF file"""
        if self.pdf:
            self.pdf.close()
            self.logger.info("PDF file closed")

    @property
    def page_count(self) -> int:
        """Get total PDF page count"""
        if self.pdf:
            return len(self.pdf.pages)
        return 0

    def get_page(self, page_num: int) -> Optional[Any]:
        """
        Get specified page

        Args:
            page_num: Page number (starting from 0)

        Returns:
            pdfplumber.Page object
        """
        if self.pdf and 0 <= page_num < self.page_count:
            return self.pdf.pages[page_num]
        return None

    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
