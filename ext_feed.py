import xml.etree.ElementTree as ET
import json
import yaml
from datetime import datetime
import time

def generate_feed(config, cache_data, output_file='feed.xml'):
    # 读取config.yaml
    # with open(config_file, 'r', encoding='utf-8') as f:
    #     config = yaml.safe_load(f)
    
    # # 读取cache.json
    # with open(cache_file, 'r', encoding='utf-8') as f:
    #     cache_data = json.load(f)
    
    # 创建RSS根元素
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    # 添加channel基本信息
    ET.SubElement(channel, 'title').text = config['blog_name']
    ET.SubElement(channel, 'link').text = config['site']
    ET.SubElement(channel, 'description').text = config['blog_signature']
    ET.SubElement(channel, 'lastBuildDate').text = format_rfc822(datetime.now())
    
    # 处理cache中的文章数据
    items = []
    for file_path, item_data in cache_data.items():
        # 检查date字段是否为空
        if not item_data.get('date'):
            continue
        
        # 解析日期字符串
        date_str = item_data['date']
        item_date = parse_date(date_str)
        
        if item_date:
            items.append({
                'title': item_data.get('title') or "无题",
                'link': item_data.get('quote_link', ''),
                'date': item_date,
                'description': item_data.get('description', ''),
                'guid': item_data.get('quote_link', '')
            })
        else:
            print(f"无法解析日期: {date_str}")
    
    # 按日期排序（最新的在前）
    items.sort(key=lambda x: x['date'], reverse=True)
    
    # 只取前10个
    items = items[:10]
    
    # 添加item到channel
    for item in items:
        item_elem = ET.SubElement(channel, 'item')
        ET.SubElement(item_elem, 'title').text = item['title']
        ET.SubElement(item_elem, 'link').text = item['link']
        ET.SubElement(item_elem, 'pubDate').text = format_rfc822(item['date'])
        ET.SubElement(item_elem, 'guid', isPermaLink='true').text = item['guid']
        
        # 处理description，使用CDATA
        description_elem = ET.SubElement(item_elem, 'description')
        description_elem.text = f"<![CDATA[{item['description']}]]>"
    
    # 生成XML
    tree = ET.ElementTree(rss)
    
    # 添加XML声明
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding='unicode')
    
    print(f"RSS feed已生成: {output_file}")

def parse_date(date_str):
    """解析多种日期格式"""
    date_formats = [
        "%y/%m/%d/%H:%M",  # 24/9/24/19:05
        "%Y/%m/%d/%H:%M",  # 2024/9/24/19:05
        "%Y/%m/%d",        # 2024/9/24
        "%y/%m/%d",        # 24/9/24
        "%Y-%m-%d",        # 2024-9-24
        "%y-%m-%d",        # 24-9-24
        "%Y/%m/%d %H:%M",  # 2024/9/24 19:05
        "%y/%m/%d %H:%M",  # 24/9/24 19:05
        "%Y-%m-%d %H:%M",  # 2024-9-24 19:05
        "%y-%m-%d %H:%M",  # 24-9-24 19:05
    ]
    
    for fmt in date_formats:
        try:
            # 尝试解析日期
            dt = datetime.strptime(date_str, fmt)
            return dt
        except ValueError:
            continue
    
    # 如果所有格式都失败，返回None
    return None

def format_rfc822(dt):
    """将datetime对象格式化为RFC 822格式"""
    # RFC 822日期格式: "Mon, 21 Apr 2025 19:16:00 +0800"
    return dt.strftime('%a, %d %b %Y %H:%M:%S +0800')

# 使用示例
if __name__ == "__main__":
    generate_feed('config.yaml', 'cache.json', 'feed.xml')