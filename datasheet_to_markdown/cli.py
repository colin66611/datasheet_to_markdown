"""CLI Interface - Command Line Tool"""

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
              help="Output directory (default: ./output)")
@click.option("--toc", is_flag=True, default=False,
              help="Generate table of contents")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Verbose output")
@click.option("--confidence", "-c", type=float, default=50,
              help="Confidence threshold 0-100 (default: 50)")
def convert(pdf_path: str, output: str, toc: bool, verbose: bool, confidence: float):
    """
    Convert datasheet PDF to Markdown document

    Examples:

        python -m datasheet_to_markdown convert input.pdf --toc --verbose

        python -m datasheet_to_markdown convert input.pdf -o ./output --confidence 60
    """
    # Validate confidence threshold
    if not 0 <= confidence <= 100:
        click.echo("Error: Confidence threshold must be between 0-100", err=True)
        sys.exit(1)

    try:
        # Create converter
        converter = DatasheetConverter(
            pdf_path=pdf_path,
            output_dir=output,
            add_toc=toc,
            confidence_threshold=confidence,
            verbose=verbose
        )

        # Execute conversion
        output_file = converter.convert()

        click.echo(f"\n✅ Conversion successful!")
        click.echo(f"📁 Output directory: {output}")
        click.echo(f"📄 Document file: {output_file}")

        # Show images directory
        images_dir = os.path.join(output, "images")
        if os.path.exists(images_dir):
            image_count = len([f for f in os.listdir(images_dir) if f.endswith(".png")])
            click.echo(f"🖼️  Image count: {image_count}")

    except Exception as e:
        click.echo(f"\n❌ Conversion failed: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.group()
def cli():
    """Datasheet to Markdown Converter - Convert chip datasheet to Markdown document"""
    pass


# Add convert command to CLI group
cli.add_command(convert)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
