import markdown

# 你的 markdown 代码
markdown_text = '''
洗う（あらう）
: **释义**：洗
: **例句**：手を洗ってから、おにぎりを食べます。
: **翻译**：我洗手之后吃了饭团。

'''

def test_markdown_rendering():
    """测试 markdown 渲染"""
    
    # 创建 markdown 实例
    html_output = markdown.markdown(
        markdown_text, 
        extensions=[
            'fenced_code', 'tables', 'footnotes', 'nl2br', 'toc', 'pymdownx.tilde', 
            'pymdownx.tasklist', 
        ]
    )
    
    print("渲染后的 HTML:")
    print(html_output)

if __name__ == "__main__":
    test_markdown_rendering()
