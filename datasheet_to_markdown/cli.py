"""CLI接口 - 命令行工具"""

import click
import os
import sys
from pathlib import Path
from datasheet_to_markdown.converter import DatasheetConverter
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="./output",
              help="输出目录（默认：./output）")
@click.option("--toc", is_flag=True, default=False,
              help="生成目录")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="详细输出")
@click.option("--confidence", "-c", type=float, default=50,
              help="置信度阈值 0-100（默认：50）")
def convert(pdf_path: str, output: str, toc: bool, verbose: bool, confidence: float):
    """
    将datasheet PDF转换为Markdown文档

    示例：

        python -m datasheet_to_markdown convert input.pdf --toc --verbose

        python -m datasheet_to_markdown convert input.pdf -o ./output --confidence 60
    """
    # 验证置信度阈值
    if not 0 <= confidence <= 100:
        click.echo("错误：置信度阈值必须在0-100之间", err=True)
        sys.exit(1)

    try:
        # 创建转换器
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=output,
            add_toc=toc,
            confidence_threshold=confidence,
            verbose=verbose
        )

        # 执行转换
        output_file = converter.convert()

        click.echo(f"\n✅ 转换成功！")
        click.echo(f"📁 输出目录: {output}")
        click.echo(f"📄 文档文件: {output_file}")

        # 显示图片目录
        images_dir = os.path.join(output, "images")
        if os.path.exists(images_dir):
            image_count = len([f for f in os.listdir(images_dir) if f.endswith(".png")])
            click.echo(f"🖼️  图片数量: {image_count}")

    except Exception as e:
        click.echo(f"\n❌ 转换失败: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.group()
def cli():
    """Datasheet to Markdown Converter - 将芯片datasheet转换为Markdown文档"""
    pass


# 添加convert命令到CLI组
cli.add_command(convert)


def main():
    """主入口"""
    cli()


if __name__ == "__main__":
    main()
