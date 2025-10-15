import yaml

# 原始 YAML 内容
yaml_content = """
extensions:
    - category
    - timeline
    - rss
"""

# 解析 YAML
data = yaml.safe_load(yaml_content)

# 转换结构：将 category 从字符串变为字典
if 'extensions' in data:
    # 找到 category 的索引
    extensions = data['extensions']
    if 'category' in extensions:
        category_index = extensions.index('category')
        # 替换为字典形式
        extensions[category_index] = {
            'category': {
                'enabled': True,
                'config': {
                    'path': '/categories',
                    'display': 'list'
                    # 添加其他配置...
                }
            }
        }

print(extensions)