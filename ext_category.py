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
            config_path: 配置文件路径
            cache_path: 缓存数据文件路径
        """
        # self.config_path = Path(config_path)
        # self.cache_path = Path(cache_path)
        self.config: Dict[str, Any] = config
        self.cache_data: Dict[str, Any] = cache_data
        self.partials: Dict[str, str] = {}
        
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载配置文件时发生错误: {e}")
    
    def load_cache_data(self) -> None:
        """加载缓存数据"""
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                self.cache_data = json.load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"缓存文件不存在: {self.cache_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"缓存文件JSON格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载缓存数据时发生错误: {e}")
    
    def load_partials(self) -> None:
        """加载部分模板"""
        partials_dir = self.config.get('partials_dir', 'partials')
        partials_path = Path(partials_dir)
        
        if not partials_path.exists():
            self.partials = {}
            return
            
        try:
            for file_path in partials_path.glob('*.mustache'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_name = file_path.stem
                    self.partials[template_name] = f.read()
        except Exception as e:
            raise RuntimeError(f"加载部分模板时发生错误: {e}")
    
    def transform_data_to_category(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            
            # 创建帖子信息
            post_info = {
                'date': post_data.get('date', ''),
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
        transformed_data = self.transform_data_to_category(self.cache_data)
        self.config['category'] = transformed_data
        
        # 加载模板
        template_dir = self.config.get("template_dir", "")
        category_template = self.config.get("category_template", "")
        template_path = Path(template_dir) / category_template
        
        template_content = self.load_template(str(template_path))
        
        # 渲染模板
        try:
            final_html = chevron.render(template_content, self.config, partials_dict=self.partials)
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
            # 加载必要的数据
            # self.load_config()
            # self.load_cache_data()
            self.load_partials()
            
            # 生成HTML
            html_content = self.generate_html()
            
            # 保存结果
            self.save_html(html_content, output_path)
            
            print("分类页面生成成功！")
            
        except Exception as e:
            raise RuntimeError(f"生成分类页面时发生错误: {e}")

# 使用示例
if __name__ == "__main__":
    # 基本用法
    generator = CategoryGenerator()
    generator.run()
    
    # 自定义配置文件路径
    # generator = CategoryGenerator("my_config.yaml", "my_cache.json")
    # generator.run("output/category.html")