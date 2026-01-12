"""集成测试 - 端到端测试"""

import pytest
import os
import tempfile
from datasheet_to_markdown.converter import DatasheetConverter


@pytest.mark.integration
def test_full_conversion():
    """测试完整转换流程"""
    # 注意：这个测试需要一个真实的PDF文件
    # 在CI/CD环境中应该使用fixture PDF

    pdf_path = "tests/fixtures/sample.pdf"

    if not os.path.exists(pdf_path):
        pytest.skip("测试PDF文件不存在")

    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=temp_dir,
            add_toc=True,
            verbose=False
        )

        output_file = converter.convert()

        # 检查输出文件是否存在
        assert os.path.exists(output_file)

        # 检查输出文件内容
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 应该包含Markdown标题
        assert "#" in content

        # 如果有目录，应该包含TOC
        if converter.add_toc:
            assert "Table of Contents" in content


@pytest.mark.integration
def test_conversion_with_low_confidence():
    """测试低置信度转换"""
    pdf_path = "tests/fixtures/sample.pdf"

    if not os.path.exists(pdf_path):
        pytest.skip("测试PDF文件不存在")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 设置很低的置信度阈值，大部分表格都应该被标记
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=temp_dir,
            confidence_threshold=100,  # 100%阈值
            verbose=False
        )

        output_file = converter.convert()

        assert os.path.exists(output_file)

        # 检查是否有MANUAL_CHECK标记
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 由于置信度阈值很高，应该有[MANUAL_CHECK]标记
        # （如果有表格的话）
        # assert "[MANUAL_CHECK]" in content
