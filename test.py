import os
import yaml
import json
import chevron
import frontmatter
import markdown
from pathlib import Path
from typing import Dict, Any, List, Optional
import re


import chevron

template_content = '''
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>{{ title }}</title>
</head>
<body>
  <header>
    <h1>{{ blog_title }}</h1>
    <hr>
  </header>

  <h2>{{ title }}</h2>
  <p><strong>分类:</strong> {{ category }} | <strong>发布日期:</strong> {{ date }}</p>
  {{# tags }}
    <span>#{{.}}</span>
  {{/ tags }}

  <main>
    {{> content }}
  </main>

  <footer>
    <p>{{ footer_note }}</p>
    <p>作者: {{ author }}</p>
    {{> fancy_banner }}
  </footer>
</body>
</html>
'''

# 将上下文改为字典格式
template_context = {
    'blog_title': 'haha',
    'category': ['test1', 'test2'],  # 或者保持为列表 
    'title': '我的博客文章',
    'date': '2024-01-01',
    'footer_note': '版权信息',
    'author': '作者名',
    'tags': ['标签1', '标签2', '标签3']
}

render_partials = {
    'content': '测试内容',
    'fancy_banner': '<div>华丽的横幅</div>'
}

out = chevron.render(template_content, template_context, partials_dict=render_partials)
print(out)