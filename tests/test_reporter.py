"""测试质量报告器"""

import io
import sys
from datasheet_to_markdown.quality.reporter import QualityReporter


def test_reporter_init():
    """测试初始化"""
    reporter = QualityReporter()
    assert reporter.total_tables == 0
    assert reporter.total_confidence == 0.0
    assert len(reporter.tables_checked) == 0


def test_reporter_report_table():
    """测试记录表格信息"""
    reporter = QualityReporter()

    # 记录一个表格
    reporter.report_table({
        "page_num": 1,
        "caption": "Test Table",
        "flask": 85.5,
        "needs_manual_check": True,
        "complexity": {"rows": 10, "cols": 3, "complexity_score": 0.5},
        "uncertain_cells": [(1, 1), (2, 2)]
    })

    assert reporter.total_tables == 1
    assert reporter.total_confidence == 85.5
    assert len(reporter.tables_checked) == 1


def test_reporter_multiple_tables():
    """测试记录多个表格"""
    reporter = QualityReporter()

    # 记录多个表格
    for i in range(5):
        reporter.report_table({
            "page_num": i + 1,
            "caption": f"Table {i}",
            "flask": 80.0 + i,
            "needs_manual_check": i % 2 == 0,
            "complexity": {"rows": 10, "cols": 3, "complexity_score": 0.5},
            "uncertain_cells": []
        })

    assert reporter.total_tables == 5
    # 从i=0开始，flask=80.0+i，所以是80+81+82+83+84=410
    assert reporter.total_confidence == 410.0


def test_reporter_get_metrics():
    """测试获取质量指标"""
    reporter = QualityReporter()

    # 添加一些测试数据
    reporter.report_table({
        "page_num": 1,
        "caption": "Table 1",
        "flask": 90.0,
        "needs_manual_check": False,
        "complexity": {"rows": 5, "cols": 3},
        "uncertain_cells": []
    })

    reporter.report_table({
        "page_num": 2,
        "caption": "Table 2",
        "flask": 70.0,
        "needs_manual_check": True,
        "complexity": {"rows": 10, "cols": 5},
        "uncertain_cells": [(0, 1), (1, 1)]
    })

    metrics = reporter.get_metrics()

    assert metrics["total_tables"] == 2
    assert metrics["manual_check_tables"] == 1
    assert metrics["manual_check_ratio"] == 0.5
    assert metrics["avg_confidence"] == 80.0
    assert metrics["coverage"] > 0


def test_reporter_print_summary_no_tables():
    """测试没有表格时的输出"""
    reporter = QualityReporter()

    # 捕获输出
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        reporter.print_summary()
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    # 应该包含质量报告部分
    assert "质量报告" in output
    assert "总表格数：0" in output


def test_reporter_print_summary_with_manual_check():
    """测试包含人工核对表格的输出"""
    reporter = QualityReporter()

    # 添加需要人工核对的表格
    reporter.report_table({
        "page_num": 1,
        "caption": "Complex Table",
        "flask": 60.0,
        "needs_manual_check": True,
        "complexity": {"rows": 25, "cols": 7, "complexity_score": 0.9},
        "uncertain_cells": [(0, 1), (1, 1)]
    })

    # 捕获输出
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        reporter.print_summary()
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    # 应该包含警告信息
    assert "警告" in output
    assert "需要人工核对的表格" in output
    assert "MANUAL_CHECK" in output
