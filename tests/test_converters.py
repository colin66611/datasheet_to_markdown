"""测试转换器"""

import pytest
from datasheet_to_markdown.converters.markdown import MarkdownConverter
from datasheet_to_markdown.converters.marker import ManualMarker


def test_heading_to_markdown():
    """测试标题转换"""
    converter = MarkdownConverter()

    # 1级标题
    md = converter.heading_to_markdown("Features", 1)
    assert md == "# Features\n\n"

    # 2级标题
    md = converter.heading_to_markdown("Description", 2)
    assert md == "## Description\n\n"

    # 3级标题
    md = converter.heading_to_markdown("Pin Functions", 3)
    assert md == "### Pin Functions\n\n"


def test_paragraph_to_markdown():
    """测试段落转换"""
    converter = MarkdownConverter()

    md = converter.paragraph_to_markdown("This is a test paragraph.")
    assert md == "This is a test paragraph.\n\n"

    # 空段落
    md = converter.paragraph_to_markdown("")
    assert md == ""


def test_list_to_markdown():
    """测试列表转换"""
    converter = MarkdownConverter()

    # 无序列表
    items = ["• Item 1", "• Item 2", "• Item 3"]
    md = converter.list_to_markdown(items, ordered=False)
    assert "- Item 1" in md
    assert "- Item 2" in md
    assert "- Item 3" in md

    # 有序列表
    items = ["1. First", "2. Second", "3. Third"]
    md = converter.list_to_markdown(items, ordered=True)
    assert "1. First" in md
    assert "2. Second" in md
    assert "3. Third" in md


def test_table_to_markdown():
    """测试表格转换"""
    converter = MarkdownConverter()

    table_data = [
        ["Name", "Type", "Description"],
        ["P1", "I/O", "Port 1"],
        ["P2", "I/O", "Port 2"]
    ]

    md = converter.table_to_markdown(table_data)

    # 检查表头
    assert "| Name | Type | Description |" in md

    # 检查分隔线
    assert "| --- | --- | --- |" in md

    # 检查数据行
    assert "| P1 | I/O | Port 1 |" in md
    assert "| P2 | I/O | Port 2 |" in md


def test_table_with_uncertain_cells():
    """测试带可疑单元格的表格转换"""
    converter = MarkdownConverter()

    table_data = [
        ["Name", "Type", "Description"],
        ["P1", "I/O", "Port 1"],
        ["P2", "", "Port 2"]  # 空单元格
    ]

    uncertain_cells = [(2, 1)]  # 第3行第2列

    md = converter.table_to_markdown(table_data, uncertain_cells=uncertain_cells)

    # 检查标记
    assert "[UNCERTAIN]" in md


def test_image_to_markdown():
    """测试图片转换"""
    converter = MarkdownConverter()

    md = converter.image_to_markdown("images/test.png", alt="Test Image")
    assert md == "![Test Image](images/test.png)\n\n"

    # 无alt文本
    md = converter.image_to_markdown("images/test.png")
    assert md == "![Image](images/test.png)\n\n"


def test_manual_marker():
    """测试人工介入标记器"""
    marker = ManualMarker()

    # 标记表格
    table_data = [
        ["A", "B"],
        ["C", ""],
        ["E", "F"]
    ]

    uncertain_cells = [(1, 1)]  # 空单元格

    marked = marker.mark_table(table_data, uncertain_cells)

    assert marked[1][1] == " [UNCERTAIN]"
    assert marked[0][0] == "A"  # 未标记的单元格不变
