"""
说说页面生成模块
将 shuoshuo.yaml 数据转换为说说HTML页面
"""
import yaml
import chevron
import markdown
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class ShuoshuoGenerator:
    """说说页面生成器"""
    
    def __init__(self, config):
        """
        初始化说说生成器
        
        Args:
            config: 配置数据
        """
        self.config = config
        
    def load_shuoshuo_data(self, shuoshuo_file: str = "shuoshuo.yaml") -> List[Dict[str, Any]]:
        """
        加载说说数据文件
        
        Args:
            shuoshuo_file: 说说数据文件路径
            
        Returns:
            说说数据列表
            
        Raises:
            FileNotFoundError: 说说文件不存在
            yaml.YAMLError: YAML格式错误
        """
        shuoshuo_path = Path(shuoshuo_file)
        if not shuoshuo_path.exists():
            raise FileNotFoundError(f"说说文件不存在: {shuoshuo_file}")
            
        try:
            # 先作为纯文本读取
            with open(shuoshuo_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            # 解析图片表
            raw_content_with_image = chevron.render(raw_content, self.config)

            # 获取markdown扩展配置
            extensions = self.config.get('md_parser_extension', [])

            # 然后解析YAML
            try:
                shuoshuo_data = yaml.safe_load(raw_content_with_image) or []
            except yaml.YAMLError as e:
                print(f"YAML解析错误: {e}")
                # 可以选择记录错误、使用默认值或重新抛出异常
                shuoshuo_data = []
            
            # 按id降序排列（最新的在前）
            # shuoshuo_data.sort(key=lambda x: x.get('id', 0), reverse=True)
            
            # 渲染一下content的内容
            for item in shuoshuo_data:
                item['content'] = markdown.markdown(item['content'], extensions=extensions)

            logger.info(f"成功加载说说数据，共 {len(shuoshuo_data)} 条说说")
            return shuoshuo_data
            
        except yaml.YAMLError as e:
            logger.error(f"YAML解析错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载说说数据时发生错误: {e}")
            raise
    
    def process_shuoshuo_data(self, shuoshuo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理说说数据，添加额外的字段
        
        Args:
            shuoshuo_data: 原始说说数据
            
        Returns:
            处理后的说说数据
        """
        processed_data = []
        
        for item in shuoshuo_data:
            try:
                processed_item = item.copy()
                
                # 确保必要的字段存在
                processed_item.setdefault('content', '')
                processed_item.setdefault('date', '')
                processed_item.setdefault('images', [])
                processed_item.setdefault('mood', '')
                processed_item.setdefault('id', 0)
                
                # 处理图片数据 - 为 Mustache 模板添加条件渲染所需的字段
                images = processed_item['images']
                if images and len(images) > 0:
                    processed_item['has_images'] = True
                    # 保持原始的 images 数组用于循环
                    processed_item['images'] = images
                else:
                    processed_item['has_images'] = False
                    processed_item['images'] = []
                
                processed_data.append(processed_item)
                
            except Exception as e:
                logger.error(f"处理说说数据时发生错误 (ID: {item.get('id', 'unknown')}): {e}")
                continue
        
        return processed_data
    
    def _load_template(self, template_path: str) -> str:
        """
        加载模板文件
        
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
    
    def run(self, shuoshuo_file: Optional[str] = None, output_path: Optional[str] = None) -> bool:
        """
        生成说说HTML页面
        
        Args:
            shuoshuo_file: 说说数据文件路径，如果为None则使用默认路径
            output_path: 输出文件路径，如果为None则使用配置中的路径
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            # 确定说说文件路径
            if shuoshuo_file is None:
                shuoshuo_file = "shuoshuo.yaml"
            
            # 加载说说数据
            shuoshuo_data = self.load_shuoshuo_data(shuoshuo_file)
            
            # 处理说说数据
            processed_shuoshuo = self.process_shuoshuo_data(shuoshuo_data)
            
            # 创建渲染数据，不修改原始配置
            render_data = self.config.copy()
            render_data['shuoshuo'] = processed_shuoshuo
            render_data['shuoshuo_count'] = len(processed_shuoshuo)
            
            # 加载模板
            template_dir = self.config.get("template_dir", "")
            shuoshuo_template = self.config.get("shuoshuo_template", "shuoshuo.mustache")
            template_path = Path(template_dir) / shuoshuo_template
            template_content = self._load_template(str(template_path))
            
            # 获取 partials
            partials = self.config.get('partials', {})

            # 渲染模板
            final_html = chevron.render(template_content, render_data, partials_dict=partials)
            
            # 确定输出路径
            if output_path is None:
                html_dir = self.config.get('html_dir', '')
                output_path = Path(html_dir) / "NOCHECK_shuoshuo.html"
            else:
                output_path = Path(output_path)
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(output_path, "w", encoding='utf-8') as f:
                f.write(final_html)
            
            logger.info(f"成功生成说说页面: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成说说页面时发生错误: {e}")
            return False

def main():
    """主函数"""
    try:
        # 注意：现在需要传入 config
        # generator = ShuoshuoGenerator(config)
        # success = generator.run()
        # return 0 if success else 1
        logger.error("请通过主程序调用 ShuoshuoGenerator")
        return 1
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

if __name__ == "__main__":
    exit(main())