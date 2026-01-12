"""表格提取器 - 使用pdfplumber提取表格（MVP简化版）"""

import os
from typing import List, Dict, Optional, Any
from datasheet_to_markdown.core.scorer import ConfidenceScorer
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class TableExtractor:
    """表格提取器（使用pdfplumber作为MVP实现）"""

    def __init__(self, pdf_path: str, page_num: int,
                 confidence_threshold: float = 50):
        """
        初始化表格提取器

        Args:
            pdf_path: PDF文件路径
            page_num: 页码（从1开始）
            confidence_threshold: 置信度阈值（0-100）
        """
        self.pdf_path = pdf_path
        self.page_num = page_num
        self.confidence_threshold = confidence_threshold
        self.scorer = ConfidenceScorer(threshold=confidence_threshold)
        self.logger = logger

    def extract(self, page: Any) -> List[Dict]:
        """
        提取表格

        Args:
            page: pdfplumber页面对象

        Returns:
            表格列表：
            [
                {
                    "data": [["Header1", "Header2"], ["Data1", "Data2"]],
                    "flask": 85.5,  # 模拟的准确率评分
                    "page": page_num,
                    "bbox": (x0, y0, x1, y1),
                    "needs_manual_check": False,
                    "uncertain_cells": [(0, 1), (2, 3)]
                }
            ]
        """
        tables = []

        try:
            # 使用pdfplumber提取表格
            extracted_tables = page.extract_tables()

            if not extracted_tables:
                return tables

            self.logger.debug(f"页面 {self.page_num}: 提取到 {len(extracted_tables)} 个表格")

            # 处理每个表格
            for i, table in enumerate(extracted_tables):
                table_dict = self._process_table(table, i)
                if table_dict:
                    tables.append(table_dict)

        except Exception as e:
            self.logger.warning(f"页面 {self.page_num}: 表格提取失败 - {e}")

        return tables

    def _process_table(self, table_data: List[List[str]], index: int) -> Optional[Dict]:
        """处理单个表格"""
        try:
            # 过滤空行和空列
            filtered_data = []
            for row in table_data:
                if row and any(cell and str(cell).strip() for cell in row):
                    filtered_data.append([str(cell) if cell else "" for cell in row])

            if not filtered_data:
                return None

            # 模拟flask评分（基于表格完整性）
            total_cells = sum(len(row) for row in filtered_data)
            non_empty_cells = sum(sum(1 for cell in row if cell and cell.strip()) for row in filtered_data)
            flask = (non_empty_cells / total_cells * 100) if total_cells > 0 else 50

            # 置信度分析
            score_result = self.scorer.score_table(filtered_data, flask)

            # 复杂度分析
            complexity = self.scorer.analyze_table_complexity(filtered_data)

            # 判断是否需要人工核对
            uncertain_ratio = len(score_result["uncertain_cells"]) / (complexity["rows"] * complexity["cols"]) if complexity["rows"] > 0 else 0
            needs_check = self.scorer.needs_manual_check(
                complexity, flask, uncertain_ratio
            )

            result = {
                "data": filtered_data,
                "flask": flask,
                "page": self.page_num,
                "index": index,
                "bbox": None,  # pdfplumber的extract_tables不返回bbox
                "needs_manual_check": needs_check,
                "uncertain_cells": score_result["uncertain_cells"],
                "complexity": complexity,
                "confidence": score_result["overall_confidence"]
            }

            self.logger.debug(
                f"表格 {index}: {complexity['rows']}行×{complexity['cols']}列, "
                f"flask={flask:.2f}, 人工核对={'是' if needs_check else '否'}"
            )

            return result

        except Exception as e:
            self.logger.error(f"处理表格失败: {e}")
            return None
