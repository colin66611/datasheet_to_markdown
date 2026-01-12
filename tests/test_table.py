"""测试表格提取器"""

import pytest
from datasheet_to_markdown.core.scorer import ConfidenceScorer


def test_confidence_scorer_init():
    """测试置信度分析器初始化"""
    scorer = ConfidenceScorer(threshold=50)
    assert scorer.threshold == 50


def test_score_empty_table():
    """测试空表格评分"""
    scorer = ConfidenceScorer()
    result = scorer.score_table([], 100)

    assert result["overall_confidence"] == 0.0
    assert len(result["uncertain_cells"]) == 0


def test_score_simple_table():
    """测试简单表格评分"""
    scorer = ConfidenceScorer()
    table_data = [
        ["Header1", "Header2", "Header3"],
        ["Data1", "Data2", "Data3"],
        ["Data4", "Data5", "Data6"]
    ]

    result = scorer.score_table(table_data, 95.0)

    # 所有单元格都有内容，应该有高置信度
    assert result["overall_confidence"] > 90
    assert len(result["uncertain_cells"]) == 0


def test_score_table_with_empty_cells():
    """测试包含空单元格的表格评分"""
    scorer = ConfidenceScorer(threshold=50)
    table_data = [
        ["Header1", "Header2"],
        ["Data1", ""],  # 空单元格
        ["Data3", "Data4"]
    ]

    result = scorer.score_table(table_data, 90.0)

    # 应该检测到空单元格
    assert len(result["uncertain_cells"]) > 0
    assert (1, 1) in result["uncertain_cells"]


def test_score_table_with_truncated_text():
    """测试包含截断文本的表格评分"""
    scorer = ConfidenceScorer(threshold=50)
    table_data = [
        ["Header1", "Header2"],
        ["Data1...", "Data2"],  # 截断文本
        ["Data3", "Data4<"]  # 以<结尾
    ]

    result = scorer.score_table(table_data, 90.0)

    # 应该检测到截断文本
    assert len(result["uncertain_cells"]) > 0


def test_is_truncated():
    """测试截断文本检测"""
    scorer = ConfidenceScorer()

    assert scorer._is_truncated("Data...") is True
    assert scorer._is_truncated("Data<") is True
    assert scorer._is_truncated("Data>") is True
    assert scorer._is_truncated("Data (continued)") is True
    assert scorer._is_truncated("Normal text") is False


def test_analyze_table_complexity():
    """测试表格复杂度分析"""
    scorer = ConfidenceScorer()
    table_data = [
        ["H1", "H2", "H3"],
        ["D1", "D2", "D3"],
        ["D4", "", "D6"]  # 包含空单元格
    ]

    complexity = scorer.analyze_table_complexity(table_data)

    assert complexity["rows"] == 3
    assert complexity["cols"] == 3
    assert complexity["has_empty"] is True
    assert complexity["empty_count"] == 1
    assert 0 <= complexity["complexity_score"] <= 1


def test_needs_manual_check():
    """测试人工核对判断"""
    scorer = ConfidenceScorer()

    # 大表格（20行以上）
    complexity1 = {"rows": 25, "cols": 5}
    assert scorer.needs_manual_check(complexity1, 90, 0) is True

    # 多列表格（6列以上）
    complexity2 = {"rows": 10, "cols": 8}
    assert scorer.needs_manual_check(complexity2, 90, 0) is True

    # 低准确率
    complexity3 = {"rows": 5, "cols": 3}
    assert scorer.needs_manual_check(complexity3, 70, 0) is True

    # 高可疑度
    complexity4 = {"rows": 5, "cols": 3}
    assert scorer.needs_manual_check(complexity4, 90, 0.6) is True

    # 正常表格
    complexity5 = {"rows": 5, "cols": 3}
    assert scorer.needs_manual_check(complexity5, 95, 0.1) is False
