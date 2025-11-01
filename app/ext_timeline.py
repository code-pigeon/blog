"""
时间线生成模块
将缓存数据转换为时间线HTML页面
"""
import json
import yaml
import chevron
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)



class TimelineGenerator:
    """时间线生成器"""
    
    # 支持的日期格式
    DATE_FORMATS = [
        "%y/%m/%d/%H:%M",  # 24/9/24/19:05
        "%Y/%m/%d/%H:%M",  # 2024/9/24/19:05
        "%Y/%m/%d",        # 2024/9/24
        "%y/%m/%d",        # 24/9/24
        "%Y-%m-%d",        # 2024-9-24
        "%Y-%m-%d %H:%M",  # 2024-9-24 19:05
        "%y-%m-%d",        # 24-09-24
        "%y-%m-%d %H:%M",  # 24-09-24 19:05
    ]
    
    def __init__(self, config, cache_data):
        """
        初始化时间线生成器
        
        Args:
            config: 配置数据
            cache_data: 缓存数据
        """
        self.config = config
        self.cache_data = cache_data
        
    def parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        解析日期字符串，支持多种格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            解析后的datetime对象，解析失败返回None
        """
        if not date_str:
            return None
            
        # 清理日期字符串中的空格
        date_str = date_str.strip()
        
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"无法解析日期字符串: {date_str}")
        return None
    
    def _load_template(self, template_path: str) -> str:
        """
        加载主模板
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            模板内容
            
        Raises:
            FileNotFoundError: 模板文件不存在
        """
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
            
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            logger.info(f"成功加载模板: {template_path}")
            return template_content
        except Exception as e:
            logger.error(f"加载模板时发生错误: {e}")
            raise
    
    def transform_cache_to_timeline(self, cache_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将缓存数据转换为时间线格式
        
        Args:
            cache_data: 原始缓存数据
            
        Returns:
            转换后的时间线数据
        """
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
            try:
                date_str = item_data.get('date')
                parsed_date = self.parse_date(date_str) if date_str else None
                
                timeline_item = {
                    "quote_link": item_data.get('quote_link', ''),
                    "quote_html_filename": item_data.get('quote_html_filename', ''),
                    "title": item_data.get('title') or '无题',
                    "category": item_data.get("category", ''),
                    "description": item_data.get('description', '')
                }
                
                if parsed_date:
                    timeline_item["date"] = parsed_date.strftime("%Y年%m月%d日")
                    items_with_date.append((parsed_date, timeline_item))
                else:
                    timeline_item["date"] = "日期丢失"
                    items_without_date.append(timeline_item)
                    
            except Exception as e:
                logger.error(f"处理条目 {file_path} 时发生错误: {e}")
                continue
        
        # 按日期排序有日期的条目（最新的在前）
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
                    try:
                        item_with_position = item.copy()
                        item_with_position["position"] = "left" if i % 2 == 0 else "right"
                        month_data["timelineItems"].append(item_with_position)
                    except Exception as e:
                        logger.error(f"处理时间线项目时发生错误: {e}")
                        continue
                
                year_data["months"].append(month_data)
            
            result["years"].append(year_data)
        
        # 处理没有日期的条目
        for i, item in enumerate(items_without_date):
            try:
                item_with_position = item.copy()
                item_with_position["position"] = "left" if i % 2 == 0 else "right"
                result["miss_date"].append(item_with_position)
            except Exception as e:
                logger.error(f"处理无日期条目时发生错误: {e}")
                continue
        
        logger.info(f"时间线数据转换完成: {len(result['years'])} 年, {len(items_without_date)} 条无日期记录")
        return result
    
    def run(self, output_path: Optional[str] = None) -> bool:
        """
        生成时间线HTML页面
        
        Args:
            output_path: 输出文件路径，如果为None则使用配置中的路径
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            # 转换数据
            transformed_data = self.transform_cache_to_timeline(self.cache_data)
            
            # 创建渲染数据，不修改原始配置
            render_data = self.config.copy()
            render_data['timeline'] = transformed_data
            render_data['has_comment'] = False
            
            # 加载模板
            template_dir = self.config.get("template_dir", "")
            timeline_template = self.config.get("timeline_template", "timeline.mustache")
            template_path = Path(template_dir) / timeline_template
            template_content = self._load_template(str(template_path))
            
            # 获取 partials
            partials = self.config.get('partials', {})
            
            # 渲染模板
            final_html = chevron.render(template_content, render_data, partials_dict=partials)
            
            # 确定输出路径
            if output_path is None:
                html_dir = self.config.get('html_dir', '')
                output_path = Path(html_dir) / "NOCHECK_timeline.html"
            else:
                output_path = Path(output_path)
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(output_path, "w", encoding='utf-8') as f:
                f.write(final_html)
            
            logger.info(f"成功生成时间线页面: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成时间线页面时发生错误: {e}")
            return False

def main():
    """主函数"""
    try:
        # 注意：现在需要传入 config 和 cache_data
        # generator = TimelineGenerator(config, cache_data)
        # success = generator.run()
        # return 0 if success else 1
        logger.error("请通过主程序调用 TimelineGenerator")
        return 1
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())