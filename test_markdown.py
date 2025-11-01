import markdown

# 你的 markdown 代码
markdown_text = '''
这是正常文本<sup>这是上标</sup>继续正常文本

例如：

- 拼音：zhōng guó<sup>①</sup>
- 数学公式：x<sup>2</sup> + y<sup>2</sup> = z<sup>2</sup>
- 化学式：H<sup>+</sup> + OH<sup>-</sup> = H<sub>2</sub>O
- 注释：这是一个重要概念<sup>[1]</sup>
'''

def test_markdown_rendering():
    """测试 markdown 渲染"""
    
    # 创建 markdown 实例
    html_output = markdown.markdown(markdown_text, extensions=['fenced_code', 'tables', 'footnotes', 'nl2br', 'toc', 'pymdownx.tilde', 'pymdownx.tasklist'])
    
    print("渲染后的 HTML:")
    print(html_output)

if __name__ == "__main__":
    test_markdown_rendering()
