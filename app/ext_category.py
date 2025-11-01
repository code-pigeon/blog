import json
import yaml
import chevron
from pathlib import Path
from typing import Dict, List, Any, Optional

class CategoryGenerator:
    """分类页面生成器"""
    
    def __init__(self, config, cache_data):
        """
        初始化分类生成器
        
        Args:
            config: 配置数据
            cache_data: 缓存数据
        """
        self.config: Dict[str, Any] = config
        self.cache_data: Dict[str, Any] = cache_data
        
    def transform_data(self, input_data):
        """
        将原始博客数据转换为按分类组织的结构
        
        Args:
            input_data: 原始博客数据字典
            
        Returns:
            dict: 转换后的分类结构数据
        """
        
        # 初始化结果数据结构
        result = {
            "category": []
        }
        
        # 使用字典来跟踪分类和子分类
        category_map = {}
        
        for file_path, post_data in input_data.items():
            # 处理日期
            date_str = post_data.get('date')
            date = date_str.split(' ')[0] if date_str and ' ' in date_str else date_str or "日期丢失"
            
            # 提取文章信息
            post_info = {
                "date": date,
                "title": post_data.get("title") or "无题",
                "quote_html_filename": post_data.get("quote_html_filename"),
                "tags": []
            }
            
            categories = post_data.get("category", [])
            
            # 处理分类和标签
            category_name = categories[0] if categories else "未分类"
            subcategory_name = categories[1] if len(categories) > 1 else None
            
            # 第三个及以后的元素作为标签
            if len(categories) > 2:
                post_info["tags"] = categories[2:]
            
            # 创建或获取分类
            if category_name not in category_map:
                new_category = {
                    "name": category_name,
                    "subcategory": [] if category_name != "未分类" else None
                }
                category_map[category_name] = new_category
            
            current_category = category_map[category_name]
            
            # 处理文章放置
            if category_name == "未分类":
                # 未分类的文章直接放在主分类下
                if "posts" not in current_category:
                    current_category["posts"] = []
                current_category["posts"].append(post_info)
            else:
                if subcategory_name:
                    # 有子分类的情况
                    # 查找是否已存在该子分类
                    subcategory = None
                    for sc in current_category["subcategory"]:
                        if sc["name"] == subcategory_name:
                            subcategory = sc
                            break
                    
                    if not subcategory:
                        # 创建新的子分类
                        subcategory = {
                            "name": subcategory_name,
                            "posts": []
                        }
                        current_category["subcategory"].append(subcategory)
                    
                    subcategory["posts"].append(post_info)
                else:
                    # 只有主分类，没有子分类
                    if "posts" not in current_category:
                        current_category["posts"] = []
                    current_category["posts"].append(post_info)
        
        # 将分类添加到结果中，确保"未分类"在最后
        sorted_categories = sorted(
            [cat for cat in category_map.values() if cat["name"] != "未分类"],
            key=lambda x: x["name"]
        )
        
        # 添加未分类（如果存在）
        if "未分类" in category_map:
            sorted_categories.append(category_map["未分类"])
        
        result["category"] = sorted_categories
        
        return result

    def transform_data0(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        将输入数据转换为分类格式
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            转换后的分类数据列表
        """
        if not isinstance(input_data, dict):
            raise ValueError("输入数据必须是字典类型")
        
        categories_dict = {}
        
        for file_path, post_data in input_data.items():
            if not isinstance(post_data, dict):
                continue
                
            # 获取分类列表
            categories = post_data.get('category', [])
            
            # 确保categories是列表类型
            if not isinstance(categories, list):
                categories = [categories] if categories else []
            
            # 确定分类名称（第一个元素），如果没有则为"未分类"
            if categories:
                category_name = str(categories[0]) if categories[0] is not None else "未分类"
                # 标签是分类列表中除第一个元素外的其他元素
                tags = [str(tag) for tag in categories[1:]] if len(categories) > 1 else []
            else:
                category_name = "未分类"
                tags = []
            
            # 创建时间
            # 如果是"23-01-01 1:23"这样的数据，那么取"23-01-01"；
            # 如果是"23-01-02"这样的数据，直接取全部；
            # 如果是None，取"日期丢失"
            date_str = post_data.get('date')
            if date_str is None:
                date = "日期丢失"
            else:
                # 如果有空格，取空格前的内容；否则取整段
                date = date_str.split(' ')[0] if ' ' in date_str else date_str


            # 创建帖子信息
            post_info = {
                'date': date,
                'title': post_data.get('title') or "无题",
                'quote_link': post_data.get('quote_link', ''),
                'quote_html_filename': post_data.get('quote_html_filename', ''),
                'tags': tags
            }
            
            # 如果该分类还不存在，则创建
            if category_name not in categories_dict:
                categories_dict[category_name] = []
            
            # 将帖子添加到对应的分类中
            categories_dict[category_name].append(post_info)
        
        # 构建最终输出格式，将"未分类"放在最后
        result = []
        uncategorized_posts = None
        
        # 先处理其他分类
        for category_name, posts in categories_dict.items():
            if category_name == "未分类":
                uncategorized_posts = posts
                continue
                
            category_obj = {
                'name': category_name,
                'posts': posts
            }
            result.append(category_obj)
        
        # 最后添加未分类
        if uncategorized_posts is not None:
            uncategorized_obj = {
                'name': "未分类",
                'posts': uncategorized_posts
            }
            result.append(uncategorized_obj)
        
        return result
    
    def load_template(self, template_path: str) -> str:
        """
        加载模板文件
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            模板内容字符串
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        except Exception as e:
            raise RuntimeError(f"加载模板文件时发生错误: {e}")
    
    def generate_html(self) -> str:
        """
        生成最终的HTML内容
        
        Returns:
            生成的HTML字符串
        """
        # 转换数据
        transformed_data = self.transform_data(self.cache_data)
        
        # 创建渲染数据，不修改原始配置
        render_data = self.config.copy()
        render_data['category'] = transformed_data
        render_data['has_comment'] = False
        
        # 加载模板
        template_dir = self.config.get("template_dir", "")
        category_template = self.config.get("category_template", "")
        template_path = Path(template_dir) / category_template
        
        template_content = self.load_template(str(template_path))
        
        # 获取 partials
        partials = self.config.get('partials', {})
        
        # 渲染模板
        try:
            final_html = chevron.render(template_content, render_data, partials_dict=partials)
            return final_html
        except Exception as e:
            raise RuntimeError(f"渲染模板时发生错误: {e}")
    
    def save_html(self, html_content: str, output_path: Optional[str] = None) -> None:
        """
        保存HTML文件
        
        Args:
            html_content: HTML内容
            output_path: 输出文件路径，如果为None则使用配置中的路径
        """
        if output_path is None:
            html_dir = self.config.get('html_dir', '')
            output_path = Path(html_dir) / "NOCHECK_category.html"
        else:
            output_path = Path(output_path)
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, "w", encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            raise RuntimeError(f"保存HTML文件时发生错误: {e}")
    
    def run(self, output_path: Optional[str] = None) -> None:
        """
        运行完整的生成流程
        
        Args:
            output_path: 可选的输出文件路径
        """
        try:
            # 生成HTML
            html_content = self.generate_html()
            
            # 保存结果
            self.save_html(html_content, output_path)
            
            print("分类页面生成成功！")
            
        except Exception as e:
            raise RuntimeError(f"生成分类页面时发生错误: {e}")

# 使用示例
if __name__ == "__main__":
    # 注意：现在需要传入 config 和 cache_data
    # generator = CategoryGenerator(config, cache_data)
    # generator.run()
    pass