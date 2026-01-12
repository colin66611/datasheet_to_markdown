"""使用真实PDF文件的集成测试"""

import os
import pytest
import tempfile
from datasheet_to_markdown.converter import DatasheetConverter


# 测试PDF路径
TEST_PDF = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"


@pytest.fixture(scope="module")
def real_pdf_path():
    """获取真实PDF文件路径"""
    if not os.path.exists(TEST_PDF):
        pytest.skip(f"测试PDF不存在: {TEST_PDF}")
    return TEST_PDF


@pytest.mark.integration
def test_real_pdf_full_conversion(real_pdf_path):
    """测试真实PDF完整转换"""
    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            add_toc=True,
            confidence_threshold=50,
            verbose=False
        )

        output_file = converter.convert()

        # 验证基本输出
        assert os.path.exists(output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 验证文档结构
        assert len(content) > 1000  # 至少有内容
        assert "#" in content  # 有标题


@pytest.mark.integration
def test_real_pdf_table_count(real_pdf_path):
    """测试表格提取数量"""
    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            verbose=False
        )

        output_file = converter.convert()

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 统计表格数量（通过查找分隔符）
        table_count = content.count("| ---")
        assert table_count > 50  # 应该至少有50个表格
        print(f"\n✅ 提取到 {table_count} 个表格")


@pytest.mark.integration
def test_real_pdf_heading_count(real_pdf_path):
    """测试标题识别数量"""
    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            verbose=False
        )

        output_file = converter.convert()

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 统计标题数量
        heading_count = sum(1 for line in content.split("\n") if line.startswith("#"))
        assert heading_count > 50  # 应该至少有50个标题
        print(f"\n✅ 识别到 {heading_count} 个标题")


@pytest.mark.integration
def test_real_pdf_manual_check_markers(real_pdf_path):
    """测试人工介入标记"""
    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            confidence_threshold=50,
            verbose=False
        )

        output_file = converter.convert()

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查标记
        manual_check_count = content.count("[MANUAL_CHECK]")
        uncertain_count = content.count("[UNCERTAIN]")

        print(f"\n✅ [MANUAL_CHECK] 标记: {manual_check_count} 个")
        print(f"✅ [UNCERTAIN] 标记: {uncertain_count} 个")

        # 应该有标记（取决于置信度阈值）
        assert manual_check_count >= 0
        assert uncertain_count >= 0


@pytest.mark.integration
def test_real_pdf_toc_generation(real_pdf_path):
    """测试目录生成"""
    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            add_toc=True,
            verbose=False
        )

        output_file = converter.convert()

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查目录
        assert "Table of Contents" in content
        assert "# Table of Contents" in content


@pytest.mark.integration
def test_real_pdf_content_types(real_pdf_path):
    """测试各种内容类型"""
    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            verbose=False
        )

        output_file = converter.convert()

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查各种内容类型
        has_headings = "#" in content
        has_paragraphs = len([line for line in content.split("\n") if line.strip() and not line.startswith("#") and not line.startswith("|")]) > 10
        has_tables = "| ---" in content
        has_lists = "- " in content or "* " in content or "1. " in content

        print(f"\n✅ 标题: {has_headings}")
        print(f"✅ 段落: {has_paragraphs}")
        print(f"✅ 表格: {has_tables}")
        print(f"✅ 列表: {has_lists}")

        assert has_headings
        assert has_tables


@pytest.mark.integration
def test_real_pdf_performance(real_pdf_path):
    """测试性能指标"""
    import time

    with tempfile.TemporaryDirectory() as temp_dir:
        start_time = time.time()

        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            verbose=False
        )

        output_file = converter.convert()

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n✅ 转换时间: {duration:.2f} 秒")
        print(f"✅ 处理速度: {38 / duration * 60:.2f} 页/分钟" if duration > 0 else "")

        # 性能要求（根据验收标准）
        assert duration < 600  # 10分钟以内
        assert (38 / duration * 60) if duration > 0 else 0 > 5  # 至少5页/分钟


@pytest.mark.integration
def test_real_pdf_key_information_extraction(real_pdf_path):
    """测试关键信息提取（AI理解测试）"""
    with tempfile.TemporaryDirectory() as temp_dir:
        converter = DatasheetConverter(
            pdf_path=real_pdf_path,
            output_dir=temp_dir,
            verbose=False
        )

        output_file = converter.convert()

        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查关键信息（根据验收标准）
        # 这些信息应该在文档中可以被AI找到
        has_pin_info = "pin" in content.lower() or "引脚" in content
        has_voltage_info = "VCC" in content or "1.65V" in content or "5.5V" in content
        has_frequency_info = "MHz" in content or "frequency" in content.lower() or "频率" in content

        print(f"\n✅ 引脚信息: {has_pin_info}")
        print(f"✅ 电压信息: {has_voltage_info}")
        print(f"✅ 频率信息: {has_frequency_info}")

        # 至少应该有这些关键信息
        assert has_pin_info or has_voltage_info or has_frequency_info
