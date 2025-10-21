import chevron
import yaml

def basic_usage():
    """基础用法示例"""
    # 简单的模板和数据
    template = """

<img data-url="{{img.隔壁姐姐做的饭菜}}" />

\{\{ shit\}\}
&#123;&#123;图片1&#125;&#125;

{{=( )=}}
```html
<img  data-url="{{图片1}}"  />
```
(={{ }}=)
"""
    
    data = {}
    data['img'] = 'test.jpg'

    # 渲染模板
    result = chevron.render(template, data)
    print("基础用法:")
    print(result)
    print()

basic_usage()

