# Markdown to HTML Converter

将 Markdown 文件转换为精美 HTML 网页的工具。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法
```bash
python3 md_to_html.py 目录名
```

### 完整参数
```bash
python3 md_to_html.py 目录名 -o 输出文件名.html -t "网页标题" --no-compress
```

### 参数说明
- `目录名`: 包含 Markdown 文件的目录路径
- `-o, --output`: 输出 HTML 文件路径 (默认: output.html)
- `-t, --title`: 网页标题 (默认: 目录名)
- `--no-compress`: 不压缩 HTML

## 示例

```bash
# 生成葫芦传奇
python3 md_to_html.py 葫芦 -o 葫芦.html -t "葫芦的传奇"

# 生成寻剑故事
python3 md_to_html.py 寻剑 -o 寻剑.html
```

## 功能特点

- ✅ 自动识别章节顺序(支持中文数字: 第一章、第二章...)
- ✅ 响应式设计，支持移动端
- ✅ 水平滚动导航栏
- ✅ 右下角工具栏(目录/返回顶部)
- ✅ 优雅的中国风样式
- ✅ HTML 压缩优化

## 文件格式

Markdown 文件命名格式:
- `第一章：标题.md`
- `第二章：标题.md`
- `终章：标题.md`