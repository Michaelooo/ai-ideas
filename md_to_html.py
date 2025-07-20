#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to HTML converter script
将目录下的 Markdown 文件转换为单个 HTML 网页
"""

import os
import re
import glob
import argparse
import markdown
from pathlib import Path
from typing import List, Tuple
import htmlmin


def extract_chapter_info(filename: str) -> Tuple[int, str]:
    """
    从文件名中提取章节信息
    支持格式: 第N章：标题.md, 终章：标题.md
    支持中文数字：一、二、三、四、五、六、七、八、九、十
    """
    name = Path(filename).stem
    
    # 终章特殊处理
    if name.startswith('终章：'):
        return (999, name)  # 终章排在最后
    
    # 中文数字映射
    chinese_to_num = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
    }
    
    # 匹配 "第N章：标题" 格式（支持阿拉伯数字）
    match = re.match(r'第([0-9]+)章：(.+)', name)
    if match:
        chapter_num = int(match.group(1))
        return (chapter_num, name)
    
    # 匹配 "第N章：标题" 格式（支持中文数字）
    match = re.match(r'第([一二三四五六七八九十])章：(.+)', name)
    if match:
        chinese_num = match.group(1)
        chapter_num = chinese_to_num.get(chinese_num, 0)
        return (chapter_num, name)
    
    # 如果不匹配章节格式，按文件名排序
    return (0, name)


def read_markdown_files(directory: str) -> List[Tuple[str, str]]:
    """
    读取目录下所有 Markdown 文件并按章节排序
    返回 [(章节标题, 内容), ...]
    """
    md_files = glob.glob(os.path.join(directory, "*.md"))
    
    if not md_files:
        raise ValueError(f"在目录 {directory} 中没有找到 Markdown 文件")
    
    # 提取章节信息并排序
    chapters = []
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapter_num, title = extract_chapter_info(file_path)
        chapters.append((chapter_num, title, content))
    
    # 按章节号排序
    chapters.sort(key=lambda x: x[0])
    
    return [(title, content) for _, title, content in chapters]


def markdown_to_html(text: str) -> str:
    """
    将 Markdown 转换为 HTML
    """
    md = markdown.Markdown(
        extensions=['extra', 'codehilite', 'toc'],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight'
            }
        }
    )
    return md.convert(text)


def create_navigation(chapters: List[Tuple[str, str]]) -> str:
    """
    创建章节导航
    """
    nav_items = []
    for i, (title, _) in enumerate(chapters, 1):
        anchor = f"chapter{i}"
        nav_items.append(f'<li><a href="#{anchor}">{title}</a></li>')
    
    return f"""
    <nav class="chapter-nav">
        <ul>
            {chr(10).join(nav_items)}
        </ul>
    </nav>
    """


def get_chinese_number(num: int) -> str:
    """
    将数字转换为中文数字
    """
    chinese_nums = {
        1: '壹', 2: '贰', 3: '叁', 4: '肆', 5: '伍',
        6: '陆', 7: '柒', 8: '捌', 9: '玖', 10: '拾',
        999: '终'  # 终章
    }
    return chinese_nums.get(num, str(num))


def create_chapter_html(title: str, content: str, chapter_num: int) -> str:
    """
    创建单个章节的 HTML
    """
    # 转换Markdown为HTML
    html_content = markdown_to_html(content)
    chinese_num = get_chinese_number(chapter_num)
    
    # 检查content是否以标题开头，如果是，则不添加额外的标题
    lines = content.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    
    # 如果第一行是标题且与文件名标题匹配，则不添加额外标题
    if first_line.startswith('# ') and title in first_line:
        return f"""
    <div id="chapter{chapter_num}" class="chapter">
        <div class="chapter-number">{chinese_num}</div>
        <div class="ink-decoration ink-top-right"></div>
        {html_content}
        <div class="ink-decoration ink-bottom-left"></div>
    </div>
    """
    else:
        # 如果没有匹配的标题，则添加文件名作为标题
        return f"""
    <div id="chapter{chapter_num}" class="chapter">
        <div class="chapter-number">{chinese_num}</div>
        <div class="ink-decoration ink-top-right"></div>
        <h1>{title}</h1>
        {html_content}
        <div class="ink-decoration ink-bottom-left"></div>
    </div>
    """


def generate_html(directory: str, title: str = None, compress: bool = True) -> str:
    """
    生成完整的 HTML 文档
    """
    # 读取 Markdown 文件
    chapters = read_markdown_files(directory)
    
    # 如果没有指定标题，使用目录名
    if not title:
        title = Path(directory).name
    
    # 创建导航
    navigation = create_navigation(chapters)
    
    # 生成章节内容
    chapter_htmls = []
    for i, (chapter_title, content) in enumerate(chapters, 1):
        chapter_html = create_chapter_html(chapter_title, content, i)
        chapter_htmls.append(chapter_html)
    
    # 使用参考模板的样式
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #34495e;
            --secondary-color: #2c3e50;
            --accent-color: #8e44ad;
            --text-color: #333;
            --light-bg: #f5f5f5;
            --card-bg: #fff;
            --border-color: #eee;
        }}

        body {{
            font-family: "Microsoft YaHei", "SimSun", serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: var(--light-bg);
            color: var(--text-color);
            position: relative;
        }}

        .chapter {{
            background-color: var(--card-bg);
            padding: 40px;
            margin-bottom: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}

        .chapter::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        }}

        h1 {{
            text-align: center;
            color: var(--secondary-color);
            font-size: 2em;
            margin-bottom: 1em;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.5em;
            position: relative;
        }}

        h1.main-title {{
            font-size: 3em;
            color: var(--primary-color);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1.5em;
            border: none;
            padding: 20px 0;
        }}

        h1.main-title::after {{
            content: "";
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        }}

        p {{
            text-indent: 2em;
            margin-bottom: 1em;
            line-height: 1.9;
        }}

        .dialog {{
            color: #444;
            font-weight: 500;
        }}

        .ink-wash {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.05;
            z-index: -1;
            background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxkZWZzPjxwYXR0ZXJuIGlkPSJwYXR0ZXJuIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0wIDAgTDQwIDQwIE0wIDQwIEw0MCAwIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI3BhdHRlcm4pIi8+PC9zdmc+');
        }}

        .chapter-image {{
            width: 100%;
            max-height: 300px;
            object-fit: cover;
            margin: 20px 0;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            opacity: 0.9;
            transition: opacity 0.3s ease;
        }}

        .chapter-image:hover {{
            opacity: 1;
        }}

        .chapter-decoration {{
            position: absolute;
            top: 10px;
            right: 10px;
            width: 100px;
            height: 100px;
            opacity: 0.1;
            pointer-events: none;
        }}

        .chapter-number {{
            position: absolute;
            top: 20px;
            left: 20px;
            font-size: 1.2em;
            color: var(--accent-color);
            font-weight: bold;
        }}

        .quote {{
            font-style: italic;
            color: #555;
            border-left: 3px solid var(--accent-color);
            padding-left: 1em;
            margin: 1.5em 0;
        }}

        .ending {{
            text-align: center;
            font-weight: bold;
            margin-top: 2em;
            color: var(--primary-color);
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .chapter {{
                padding: 20px;
            }}
            h1.main-title {{
                font-size: 2em;
            }}
        }}

        .ink-decoration {{
            position: absolute;
            width: 150px;
            height: 150px;
            background-size: contain;
            background-repeat: no-repeat;
            opacity: 0.1;
            z-index: -1;
        }}

        .ink-top-right {{
            top: 20px;
            right: 20px;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBkPSJNMTAgOTBDMzAgNzAgNTAgNTAgOTAgMTBDOTUgNSA5OSAxIDk5IDFDOTkgMSA5NSA1IDkwIDEwQzUwIDUwIDMwIDcwIDEwIDkwWiIgZmlsbD0iIzMzMyIvPjwvc3ZnPg==');
        }}

        .ink-bottom-left {{
            bottom: 20px;
            left: 20px;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBkPSJNOTAgMTBDNzAgMzAgNTAgNTAgMTAgOTBDNSA5NSAxIDk5IDEgOTlDMSA5OSA1IDk1IDEwIDkwQzUwIDUwIDcwIDMwIDkwIDEwWiIgZmlsbD0iIzMzMyIvPjwvc3ZnPg==');
        }}

        .chapter-nav {{
            position: sticky;
            top: 20px;
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            z-index: 100;
            overflow-x: auto;
            white-space: nowrap;
        }}

        .chapter-nav::-webkit-scrollbar {{
            height: 6px;
        }}

        .chapter-nav::-webkit-scrollbar-track {{
            background: var(--light-bg);
            border-radius: 3px;
        }}

        .chapter-nav::-webkit-scrollbar-thumb {{
            background: var(--accent-color);
            border-radius: 3px;
        }}

        .chapter-nav ul {{
            display: flex;
            list-style: none;
            padding: 0;
            margin: 0;
            flex-wrap: nowrap;
        }}

        .chapter-nav a {{
            text-decoration: none;
            color: var(--primary-color);
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
            transition: all 0.3s ease;
            margin: 0 4px;
            white-space: nowrap;
            display: block;
        }}

        .chapter-nav a:hover {{
            background-color: var(--light-bg);
            color: var(--accent-color);
        }}

        /* 右下角工具按钮 */
        .floating-tools {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 1000;
        }}

        .tool-btn {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: var(--accent-color);
            color: white;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }}

        .tool-btn:hover {{
            background-color: var(--secondary-color);
            transform: scale(1.1);
        }}

        .toc-popup {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            z-index: 1001;
            max-width: 400px;
            max-height: 70vh;
            overflow-y: auto;
            display: none;
        }}

        .toc-popup.show {{
            display: block;
        }}

        .toc-popup h3 {{
            margin: 0 0 15px 0;
            color: var(--secondary-color);
            text-align: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
        }}

        .toc-popup ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .toc-popup li {{
            margin: 8px 0;
        }}

        .toc-popup a {{
            text-decoration: none;
            color: var(--text-color);
            padding: 8px 12px;
            border-radius: 6px;
            display: block;
            transition: all 0.3s ease;
        }}

        .toc-popup a:hover {{
            background-color: var(--light-bg);
            color: var(--accent-color);
        }}

        .toc-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1000;
            display: none;
        }}

        .toc-overlay.show {{
            display: block;
        }}

        /* 响应式调整 */
        @media (max-width: 768px) {{
            .floating-tools {{
                bottom: 20px;
                right: 20px;
            }}
            
            .tool-btn {{
                width: 45px;
                height: 45px;
                font-size: 16px;
            }}
            
            .toc-popup {{
                max-width: 90vw;
                max-height: 80vh;
            }}
        }}

        /* 代码高亮样式 */
        .highlight {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 1em;
            margin: 1em 0;
            overflow-x: auto;
        }}

        pre {{
            margin: 0;
            font-family: 'Courier New', monospace;
        }}

        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}

        blockquote {{
            border-left: 3px solid var(--accent-color);
            padding-left: 1em;
            margin: 1.5em 0;
            font-style: italic;
            color: #555;
        }}
    </style>
</head>
<body>
    <div class="ink-wash"></div>
    <h1 class="main-title">{title}</h1>
    
    {navigation}

    {chr(10).join(chapter_htmls)}

    <!-- 右下角工具按钮 -->
    <div class="floating-tools">
        <button class="tool-btn" id="tocBtn" title="目录">
            <span>☰</span>
        </button>
        <button class="tool-btn" id="backToTopBtn" title="返回顶部">
            <span>↑</span>
        </button>
    </div>

    <!-- TOC弹窗遮罩层 -->
    <div class="toc-overlay" id="tocOverlay"></div>
    
    <!-- TOC弹窗 -->
    <div class="toc-popup" id="tocPopup">
        <h3>目录</h3>
        <ul id="tocList">
            {chr(10).join([f'<li><a href="#chapter{i+1}">{title}</a></li>' for i, (title, _) in enumerate(chapters)])}
        </ul>
    </div>

    <script>
        // 平滑滚动效果
        document.querySelectorAll('.chapter-nav a, .toc-popup a').forEach(anchor => {{
            anchor.addEventListener('click', function(e) {{
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {{
                    window.scrollTo({{
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    }});
                    // 如果是TOC链接，关闭TOC弹窗
                    if (this.closest('.toc-popup')) {{
                        hideToc();
                    }}
                }}
            }});
        }});

        // TOC相关功能
        const tocBtn = document.getElementById('tocBtn');
        const tocOverlay = document.getElementById('tocOverlay');
        const tocPopup = document.getElementById('tocPopup');

        function showToc() {{
            tocOverlay.classList.add('show');
            tocPopup.classList.add('show');
        }}

        function hideToc() {{
            tocOverlay.classList.remove('show');
            tocPopup.classList.remove('show');
        }}

        tocBtn.addEventListener('click', showToc);
        tocOverlay.addEventListener('click', hideToc);

        // ESC键关闭TOC
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                hideToc();
            }}
        }});

        // 返回顶部功能
        const backToTopBtn = document.getElementById('backToTopBtn');
        
        backToTopBtn.addEventListener('click', function() {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});

        // 滚动时显示/隐藏返回顶部按钮
        window.addEventListener('scroll', function() {{
            if (window.pageYOffset > 300) {{
                backToTopBtn.style.opacity = '1';
            }} else {{
                backToTopBtn.style.opacity = '0.7';
            }}
        }});
    </script>
</body>
</html>"""

    # 压缩HTML
    if compress:
        return htmlmin.minify(html_template, remove_comments=True, remove_empty_space=True)
    else:
        return html_template


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='将 Markdown 文件转换为 HTML 网页')
    parser.add_argument('directory', help='包含 Markdown 文件的目录路径')
    parser.add_argument('-o', '--output', help='输出 HTML 文件路径', default='output.html')
    parser.add_argument('-t', '--title', help='网页标题')
    parser.add_argument('--no-compress', action='store_true', help='不压缩 HTML')
    
    args = parser.parse_args()
    
    try:
        # 检查目录是否存在
        if not os.path.isdir(args.directory):
            raise ValueError(f"目录不存在: {args.directory}")
        
        # 生成 HTML
        print(f"正在处理目录: {args.directory}")
        html_content = generate_html(
            args.directory, 
            args.title, 
            compress=not args.no_compress
        )
        
        # 写入文件
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML 文件已生成: {args.output}")
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())