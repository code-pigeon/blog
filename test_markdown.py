import markdown

# 你的 markdown 代码
markdown_text = '''
当初最开始搭建博客的时候，其实没想要评论功能，但抵不住人的无限欲望，博客搭完了之后，还是觉得很寂寞，于是想着搞个评论系统，选择的过程就不说了，在往期文章[v1.0.3改版日志——评论系统的选择](v1.0.3改版日志——评论系统的选择.html)里都有提到。最后选择了Valine，这个是基于LeanCloud云服务平台开发的，有一定的免费额度，像我这个博客，一共就没多少访客，也够用了。

然后在1月份的时候，收到了LeanCloud的邮件：

> **关于 LeanCloud 停止对外提供服务的通知**
> 
> 尊敬的 LeanCloud 用户：
> 感谢您一直以来对 LeanCloud 的信任与支持。自平台上线以来，我们陪伴并见证了无数开发者的成长与创新，能与大家共同走过这十余年，我们深感荣幸。
> 
> 为了团队能聚焦打造更优质的产品，经过慎重考虑，我们决定逐步停止 LeanCloud 的服务。
> 
> ...

是的教案设计 ~~我才刚把评论系统搭好没多久你怎么就寄了。~~ 及时了解收到了

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
