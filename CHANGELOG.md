# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-12

### Added
- Table quality improvements and bug fixes
- Better handling of empty columns in table extraction
- Improved cell content cleaning (removes extra whitespace and line breaks)
- Enhanced table structure validation
- Better confidence scoring for table cells
- Internationalization support (English translations)
- Bilingual README.md (English and Chinese)
- CHANGELOG.md for tracking version changes

### Changed
- Improved table extraction accuracy
- Better handling of multi-line cells
- Enhanced PDF parsing robustness
- Code documentation translated to English
- User-facing messages now in English

### Fixed
- Fixed table column alignment issues
- Fixed empty column detection and removal
- Fixed cell content truncation problems
- Fixed table boundary detection
- Improved handling of complex table structures
- Fixed issues with nested table extraction
- Better handling of merged cells in PDF tables

### Technical
- Updated core parsing modules with better error handling
- Enhanced confidence scoring algorithm
- Improved markdown generation for tables
- Better logging and debugging output
- Code refactoring for improved maintainability

## [0.1.0] - Initial Release

### Features
- PDF to Markdown conversion for chip datasheets
- Intelligent section recognition (regex + font analysis)
- High-precision table extraction (camelot engine)
- Confidence scoring system
- Manual review marking mechanism
- Automatic header/footer filtering
- Optional table of contents generation
- CLI interface with multiple options

### Project Structure
- Core modules for parsing, classification, and extraction
- Converter modules for Markdown generation
- Quality modules for confidence assessment
- Utility modules for logging and helpers

---

[Unreleased]: https://github.com/colin66611/datasheet_to_markdown/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/colin66611/datasheet_to_markdown/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/colin66611/datasheet_to_markdown/releases/tag/v0.1.0
