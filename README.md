# Datasheet to Markdown

[English](#english) | [中文](#中文)

---

## English

Convert chip datasheet (PDF format) to complete, readable Markdown documents.

## Features

- Complete document structure (headings, paragraphs, lists, tables, images)
- Intelligent section recognition (regex matching + font analysis)
- High-precision table extraction (camelot engine)
- Confidence scoring system
- Manual review marking mechanism
- Automatic header/footer filtering
- Optional table of contents generation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m datasheet_to_markdown convert input.pdf --output ./output --toc
```

## Project Structure

```
datasheet_to_markdown/
├── core/           # Core modules (parsing, classification, extraction)
├── converters/     # Converters (Markdown generation)
├── quality/        # Quality modules (confidence, marking)
└── utils/          # Utility modules
```

## Development

```bash
# Run tests
pytest tests/

# Run tests with coverage report
pytest --cov=datasheet_to_markdown tests/
```

## License

MIT License

---

## 中文

将芯片datasheet（PDF格式）转换为完整的、可读的Markdown文档。

## 特性

- ✅ 完整文档结构（标题、段落、列表、表格、图片）
- ✅ 智能章节识别（正则匹配 + 字体分析）
- ✅ 高精度表格提取（camelot引擎）
- ✅ 置信度评分系统
- ✅ 人工介入标记机制
- ✅ 自动页眉页脚过滤
- ✅ 可选目录生成

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python -m datasheet_to_markdown convert input.pdf --output ./output --toc
```

## 项目结构

```
datasheet_to_markdown/
├── core/           # 核心模块（解析、分类、提取）
├── converters/     # 转换器（Markdown生成）
├── quality/        # 质量模块（置信度、标记）
└── utils/          # 工具模块
```

## 开发

```bash
# 运行测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest --cov=datasheet_to_markdown tests/
```

## 许可证

MIT License
