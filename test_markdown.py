import markdown

# 你的 markdown 代码
markdown_text = '''
洗う（あらう）

1. 一
    这是1
    这是2
2. 哈哈哈
    这是1
    这是2

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
