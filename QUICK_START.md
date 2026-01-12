# 快速开始指南

## 安装

```bash
# 克隆仓库
git clone git@github.com:colin66611/datasheet_to_markdown.git
cd datasheet_to_markdown

# 安装依赖
pip install -r requirements.txt
```

## 使用

### 基础用法

```bash
# 转换PDF为Markdown
python -m datasheet_to_markdown.cli convert input.pdf
```

### 高级选项

```bash
# 指定输出目录
python -m datasheet_to_markdown.cli convert input.pdf --output ./output

# 生成目录
python -m datasheet_to_markdown.cli convert input.pdf --toc

# 详细输出
python -m datasheet_to_markdown.cli convert input.pdf --verbose

# 调整置信度阈值
python -m datasheet_to_markdown.cli convert input.pdf --confidence 60
```

### 完整示例

```bash
python -m datasheet_to_markdown.cli convert \
  /path/to/txe8124-q1(en).pdf \
  --output ./output \
  --toc \
  --verbose
```

## 输出

转换成功后会生成:

- `output/datasheet.md` - 完整的Markdown文档
- `output/images/` - 提取的图片（如果有）
- CLI质量报告 - 显示表格数量、置信度、覆盖率等

## 质量标记

生成的Markdown中会包含:

- `[MANUAL_CHECK]` - 需要人工核对的表格
- `[UNCERTAIN]` - 可疑单元格

使用编辑器搜索这些标记可以快速定位需要检查的内容。

## 测试

```bash
# 运行单元测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest --cov=datasheet_to_markdown tests/
```

## 已知问题

1. **表格准确率**: 约70%的表格需要人工核对
2. **图片**: 当前版本未实际保存图片
3. **标题识别**: 部分短词（如"GND"）被误识别为标题

详细内容请查看 [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md)
