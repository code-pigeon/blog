import chevron
import yaml

def basic_usage():
    """基础用法示例"""
    # 简单的模板和数据
    template = """
- id: 3
  content: "今天天气真好，出门散步看到了美丽的日落。分享给大家！🌇"
  date: "2023-10-27 08:00"
  images:
    - "{{image_table.test1}}"
    - "{{image_table.test2}}"
    - "{{image_table.test3}}"
  mood: "😊"

- id: 2
  content: "刚刚读到了一篇关于 **静态站点生成** 的精彩文章，受益匪浅。是时候优化一下我的博客构建流程了。"
  date: "2023-10-26 08:00"
  images: 
  mood: "🤔"

- id: 1
  content: "Hello, Shuo Shuo! 这是我的第一条动态。"
  date: "2023-10-25 08:00"
  images: 
  mood: "🎉"

"""
    
    data = {}
    data['image_table'] = {
        'test1': 'img1',
        'test2': 'img2',
        'test3': 'img3',
        'test4': 'img4',
        'test5': 'img5',
    }

    # 渲染模板
    result = chevron.render(template, data)
    print("基础用法:")
    print(result)
    print()

basic_usage()

