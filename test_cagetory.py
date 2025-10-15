def transform_data(input_data):
    # 用于存储分类数据的字典
    categories_dict = {}
    
    for file_path, post_data in input_data.items():
        # 获取分类列表
        categories = post_data.get('category', [])
        
        # 确定分类名称（第一个元素），如果没有则为"未分类"
        if categories:
            category_name = categories[0]
            # 标签是分类列表中除第一个元素外的其他元素
            tags = categories[1:]
        else:
            category_name = "未分类"
            tags = []
        
        # 创建帖子信息
        post_info = {
            'date': post_data.get('date', ''),
            'title': post_data.get('title', ''),
            'quote_link': post_data.get('quote_link', ''),
            'quote_html_filename': post_data.get('quote_html_filename', ''),
            'tags': tags
        }
        
        # 如果该分类还不存在，则创建
        if category_name not in categories_dict:
            categories_dict[category_name] = []
        
        # 将帖子添加到对应的分类中
        categories_dict[category_name].append(post_info)
    
    # 构建最终输出格式
    result = {
        'category': []
    }
    
    for category_name, posts in categories_dict.items():
        category_obj = {
            'name': category_name,
            'posts': posts
        }
        result['category'].append(category_obj)
    
    return result

# 测试数据
input_data = {
  "D:/DataDisk/workspace/blog/md/IGNORE_test爱情.md": {
    "file_updated": 1760229183.3667588,
    "should_build": False,
    "title": "深入理解生成器",
    "category": ['文章', '技术博客', '生成器'],
    "date": "25/04/27/23:22",
    "updated": None,
    "link": "https://code-pigeon.github.io/blog/html/IGNORE_test爱情.html",
    "quote_link": "https://code-pigeon.github.io/blog/html/IGNORE_test%E7%88%B1%E6%83%85.html",
    "description": "**深入理解生成器** 内容……"
  },
  "D:/DataDisk/workspace/blog/md/index.md": {
    "file_updated": 1760507330.4170244,
    "should_build": False,
    "title": "我的第一篇博客",
    "category": [],
    "date": None,
    "updated": None,
    "link": "https://code-pigeon.github.io/blog/html/index.html",
    "quote_link": "https://code-pigeon.github.io/blog/html/index.html",
    "description": "所以说其实部分模板中不能嵌套部分模板？ "
  }
}

# 转换数据
output_data = transform_data(input_data)

# 打印结果
import json
print(json.dumps(output_data, ensure_ascii=False, indent=2))