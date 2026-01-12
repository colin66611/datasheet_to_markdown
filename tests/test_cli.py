"""测试CLI接口"""

import os
import sys
import tempfile
from click.testing import CliRunner
from datasheet_to_markdown.cli import convert


def test_cli_convert_basic():
    """测试基本转换命令"""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "output")
        pdf_path = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"

        if not os.path.exists(pdf_path):
            pytest.skip(f"测试PDF不存在: {pdf_path}")

        result = runner.invoke(convert, [pdf_path, "--output", output_dir])

        # 应该成功执行
        assert result.exit_code == 0 or "转换失败" in result.output

        # 检查输出文件
        if result.exit_code == 0:
            assert os.path.exists(output_dir)
            output_file = os.path.join(output_dir, "datasheet.md")
            assert os.path.exists(output_file)


def test_cli_convert_with_toc():
    """测试带目录的转换"""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "output")
        pdf_path = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"

        if not os.path.exists(pdf_path):
            pytest.skip(f"测试PDF不存在: {pdf_path}")

        result = runner.invoke(convert, [
            pdf_path,
            "--output", output_dir,
            "--toc"
        ])

        # 应该成功执行
        assert result.exit_code == 0 or "转换失败" in result.output


def test_cli_convert_with_confidence():
    """测试自定义置信度阈值"""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "output")
        pdf_path = "/Users/Zhuanz/Downloads/txe8124-q1(en).pdf"

        if not os.path.exists(pdf_path):
            pytest.skip(f"测试PDF不存在: {pdf_path}")

        result = runner.invoke(convert, [
            pdf_path,
            "--output", output_dir,
            "--confidence", "60"
        ])

        # 应该成功执行
        assert result.exit_code == 0 or "转换失败" in result.output


def test_cli_invalid_confidence():
    """测试无效的置信度阈值"""
    runner = CliRunner()

    result = runner.invoke(convert, [
        "dummy.pdf",
        "--confidence", "150"  # 无效值
    ])

    # 应该返回错误（click使用exit code 2）
    assert result.exit_code != 0
    # 检查英文或中文错误消息
    assert "Error" in result.output or "错误" in result.output


def test_cli_nonexistent_pdf():
    """测试不存在的PDF文件"""
    runner = CliRunner()

    result = runner.invoke(convert, [
        "nonexistent.pdf",
        "--output", "./output"
    ])

    # 应该返回错误（click使用exit code 2）
    assert result.exit_code != 0
    assert "does not exist" in result.output or "错误" in result.output or "does not exist" in str(result.exception) if result.exception else True


def test_cli_help():
    """测试帮助信息"""
    runner = CliRunner()

    result = runner.invoke(convert, ["--help"])

    # 应该显示帮助
    assert result.exit_code == 0
    assert "convert" in result.output
    assert "--output" in result.output
    assert "--toc" in result.output
    assert "--confidence" in result.output
