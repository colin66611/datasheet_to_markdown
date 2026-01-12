"""测试主编排器 (DatasheetConverter)"""

import os
import tempfile
import pytest
from datasheet_to_markdown.converter import DatasheetConverter


@pytest.mark.integration
def test_converter_basic_conversion():
    """测试基本转换功能"""
    pdf_path = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"

    if not os.path.exists(pdf_path):
        pytest.skip(f"测试PDF不存在: {pdf_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=temp_dir,
            add_toc=False,
            verbose=False
        )

        output_file = converter.convert()

        # 验证输出文件存在
        assert os.path.exists(output_file)
        assert output_file.endswith("datasheet.md")

        # 验证文件内容不为空
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 0

        # 应该包含一些基本结构
        assert "#" in content  # 至少有标题


@pytest.mark.integration
def test_converter_with_toc():
    """测试带目录的转换"""
    pdf_path = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"

    if not os.path.exists(pdf_path):
        pytest.skip(f"测试PDF不存在: {pdf_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=temp_dir,
            add_toc=True,
            verbose=False
        )

        output_file = converter.convert()

        # 验证输出文件包含目录
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Table of Contents" in content


@pytest.mark.integration
def test_converter_custom_confidence():
    """测试自定义置信度阈值"""
    pdf_path = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"

    if not os.path.exists(pdf_path):
        pytest.skip(f"测试PDF不存在: {pdf_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=temp_dir,
            confidence_threshold=80,  # 高阈值
            verbose=False
        )

        output_file = converter.convert()

        # 验证输出文件存在
        assert os.path.exists(output_file)


@pytest.mark.integration
def test_converter_creates_images_dir():
    """测试图片目录创建"""
    pdf_path = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"

    if not os.path.exists(pdf_path):
        pytest.skip(f"测试PDF不存在: {pdf_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=temp_dir,
            verbose=False
        )

        converter.convert()

        # 验证图片目录被创建
        images_dir = os.path.join(temp_dir, "images")
        assert os.path.exists(images_dir)


@pytest.mark.integration
def test_converter_handles_invalid_pdf():
    """测试处理无效PDF"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个假PDF文件
        fake_pdf = os.path.join(temp_dir, "fake.pdf")
        with open(fake_pdf, "w") as f:
            f.write("This is not a PDF file")

        converter = DatasheetConverter(
            pdf_path=fake_pdf,
            output_dir=temp_dir,
            verbose=False
        )

        # 应该抛出异常
        with pytest.raises(Exception):
            converter.convert()
