# Quick Start Guide

## Installation

```bash
# Clone repository
git clone git@github.com:colin66611/datasheet_to_markdown.git
cd datasheet_to_markdown

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Convert PDF to Markdown
python -m datasheet_to_markdown.cli convert input.pdf
```

### Advanced Options

```bash
# Specify output directory
python -m datasheet_to_markdown.cli convert input.pdf --output ./output

# Generate table of contents
python -m datasheet_to_markdown.cli convert input.pdf --toc

# Verbose output
python -m datasheet_to_markdown.cli convert input.pdf --verbose

# Adjust confidence threshold
python -m datasheet_to_markdown.cli convert input.pdf --confidence 60
```

### Complete Example

```bash
python -m datasheet_to_markdown.cli convert \
  /path/to/txe8124-q1(en).pdf \
  --output ./output \
  --toc \
  --verbose
```

## Output

After successful conversion, the following will be generated:

- `output/datasheet.md` - Complete Markdown document
- `output/images/` - Extracted images (if any)
- CLI quality report - Displays table count, confidence, coverage, etc.

## Quality Markers

The generated Markdown will include:

- `[MANUAL_CHECK]` - Tables requiring manual review
- `[UNCERTAIN]` - Suspicious cells

Use your editor's search function to quickly locate content that needs checking.

## Testing

```bash
# Run unit tests
pytest tests/

# Run tests with coverage report
pytest --cov=datasheet_to_markdown tests/
```

## Known Issues

1. **Table Accuracy**: Approximately 70% of tables require manual verification
2. **Images**: Current version does not actually save images
3. **Heading Recognition**: Some short words (e.g., "GND") are incorrectly identified as headings

For detailed information, see [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md)
