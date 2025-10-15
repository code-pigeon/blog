import json
import yaml
import chevron
from pathlib import Path
from datetime import datetime

def parse_date(date_str):
    """解析日期字符串，支持多种格式"""
    if not date_str:
        return None
        
    formats = [
        "%y/%m/%d/%H:%M",  # 24/9/24/19:05
        "%Y/%m/%d/%H:%M",  # 2024/9/24/19:05
        "%Y/%m/%d",        # 2024/9/24
        "%y/%m/%d",        # 24/9/24
        "%Y-%m-%d",        # 2024-9-24
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def transform_cache_to_timeline(cache_data):
    """将缓存数据转换为时间线格式"""
    result = {
        "years": [],
        "miss_date": []
    }
    
    # 按年份和月份组织数据
    year_dict = {}
    
    # 处理有日期的条目
    items_with_date = []
    items_without_date = []
    
    for file_path, item_data in cache_data.items():
        date_str = item_data.get('date')
        parsed_date = parse_date(date_str) if date_str else None
        
        timeline_item = {
            "link": item_data.get('link', ''),
            "title": item_data.get('title', ''),
            "description": item_data.get('description', '')
        }
        
        if parsed_date:
            timeline_item["date"] = parsed_date.strftime("%Y年%m月%d日")
            items_with_date.append((parsed_date, timeline_item))
        else:
            timeline_item["date"] = "日期丢失"
            items_without_date.append(timeline_item)
    
    # 按日期排序有日期的条目
    items_with_date.sort(key=lambda x: x[0], reverse=True)
    
    # 组织有日期的条目到年份和月份结构中
    for parsed_date, timeline_item in items_with_date:
        year = parsed_date.strftime("%Y")
        month = parsed_date.strftime("%m").lstrip('0')  # 去掉前导零
        
        if year not in year_dict:
            year_dict[year] = {}
        
        if month not in year_dict[year]:
            year_dict[year][month] = []
        
        year_dict[year][month].append(timeline_item)
    
    # 构建最终的年月结构
    for year in sorted(year_dict.keys(), reverse=True):
        year_data = {
            "year": year,
            "months": []
        }
        
        for month in sorted(year_dict[year].keys(), key=int, reverse=True):
            month_data = {
                "month": month,
                "timelineItems": []
            }
            
            # 为每个时间线项目添加position（左右交替）
            items = year_dict[year][month]
            for i, item in enumerate(items):
                item_with_position = item.copy()
                item_with_position["position"] = "left" if i % 2 == 0 else "right"
                month_data["timelineItems"].append(item_with_position)
            
            year_data["months"].append(month_data)
        
        result["years"].append(year_data)
    
    # 处理没有日期的条目
    for i, item in enumerate(items_without_date):
        item_with_position = item.copy()
        item_with_position["position"] = "left" if i % 2 == 0 else "right"
        result["miss_date"].append(item_with_position)
    
    return result

# 示例数据


config = {}
cache_data = {}

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

with open("cache.json", 'r', encoding='utf-8') as f:
    cache_data = json.load(f)


timeline_template_path = config.get("template_dir") + config.get("timeline_template")
template = ""
with open(timeline_template_path, 'r', encoding='utf-8') as f:
    template = f.read()


# 转换数据
transformed_data = transform_cache_to_timeline(cache_data)

config['timeline'] = transformed_data

partials_dir = config.get('partials_dir', 'partials')

partials = {}

for file_path in Path(partials_dir).glob('*.mustache'):
    with open(file_path, 'r', encoding='utf-8') as f:
        template_name = file_path.stem
        partials[template_name] = f.read()


final_html = chevron.render(template, config, partials_dict=partials)

with open(config['html_dir'] + "NOCHECK_timeline.html", "w", encoding='utf-8') as f:
    f.write(final_html)

# 打印结果
# print(json.dumps(transformed_data, ensure_ascii=False, indent=2))