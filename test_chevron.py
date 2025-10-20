import chevron
import yaml

def basic_usage():
    """基础用法示例"""
    # 简单的模板和数据
    template = """<img data-url="{{img.隔壁姐姐做的饭菜}}" />"""
    with open('image-table.yaml', 'r', encoding='utf-8') as f:
        img = yaml.safe_load(f)
    
    print(img)
    data = {}
    data['img'] = img

    # 渲染模板
    result = chevron.render(template, data)
    print("基础用法:")
    print(result)
    print()

basic_usage()

