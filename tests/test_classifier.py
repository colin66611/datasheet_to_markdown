"""测试内容块分类器"""

import pytest
from datasheet_to_markdown.core.classifier import (
    ContentBlockClassifier,
    ContentType,
    ContentBlock
)


def test_content_type_enum():
    """测试内容类型枚举"""
    assert ContentType.HEADING.value == "heading"
    assert ContentType.PARAGRAPH.value == "paragraph"
    assert ContentType.LIST.value == "list"
    assert ContentType.TABLE.value == "table"
    assert ContentType.IMAGE.value == "image"


def test_content_block_creation():
    """测试内容块创建"""
    block = ContentBlock(
        type=ContentType.HEADING,
        content="Test Heading",
        page_num=1,
        bbox=(0, 0, 100, 50),
        heading_level=1
    )

    assert block.type == ContentType.HEADING
    assert block.content == "Test Heading"
    assert block.page_num == 1
    assert block.heading_level == 1
    assert block.needs_manual_check is False


def test_heading_level_extraction():
    """测试标题层级提取"""
    classifier = ContentBlockClassifier(None, 1, 800)

    # 1级标题
    assert classifier._extract_heading_level("1. Features") == 1

    # 2级标题
    assert classifier._extract_heading_level("2.1 Description") == 2

    # 3级标题
    assert classifier._extract_heading_level("3.1.2 Pin Functions") == 3


def test_list_detection():
    """测试列表检测"""
    classifier = ContentBlockClassifier(None, 1, 800)

    # 无序列表
    assert classifier._is_list("• Item 1") is True
    assert classifier._is_list("- Item 1") is True
    assert classifier._is_list("* Item 1") is True

    # 有序列表
    assert classifier._is_list("1. Item 1") is True
    assert classifier._is_list("1) Item 1") is True

    # 非列表
    assert classifier._is_list("This is a paragraph") is False
    assert classifier._is_list("") is False


def test_footer_detection():
    """测试页眉页脚检测"""
    classifier = ContentBlockClassifier(None, 1, 800)

    # 页码
    block1 = ContentBlock(
        type=ContentType.PARAGRAPH,
        content="1",
        page_num=1,
        bbox=(0, 750, 100, 800)  # 底部
    )
    assert classifier._is_footer(block1) is True

    # 包含"Page"的文本
    block2 = ContentBlock(
        type=ContentType.PARAGRAPH,
        content="Page 1",
        page_num=1,
        bbox=(0, 750, 100, 800)
    )
    assert classifier._is_footer(block2) is True

    # 正常段落
    block3 = ContentBlock(
        type=ContentType.PARAGRAPH,
        content="This is a normal paragraph",
        page_num=1,
        bbox=(0, 400, 500, 450)
    )
    assert classifier._is_footer(block3) is False
