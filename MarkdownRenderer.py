import os
import yaml
import json
import chevron
import frontmatter
import markdown
from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, Any, List, Optional
import html
import re

class SmartExcerptGenerator:
    """
    智能文章简介生成器
    """
    
    def __init__(self, max_length: int = 200, preserve_formatting: bool = True,
                 line_break_strategy: str = "smart"):
        """
        初始化生成器
        
        Args:
            max_length: 简介最大长度
            preserve_formatting: 是否保留基本格式
            line_break_strategy: 换行处理策略
                - "preserve": 保留所有换行
                - "compact": 所有换行转空格
                - "smart": 智能合并（默认）
        """
        self.max_length = max_length
        self.preserve_formatting = preserve_formatting
        self.line_break_strategy = line_break_strategy
        
        # 配置参数
        self.sentence_enders = ['。', '！', '？', '.', '!', '?']
        self.word_separators = ['，', ',', ' ']
        
        # 编译正则表达式
        self._complex_elements_patterns = [
            (re.compile(r'<pre>[\s\S]*?</pre>', re.IGNORECASE), ''),
            (re.compile(r'<code>[\s\S]*?</code>', re.IGNORECASE), ''),
            (re.compile(r'<img[^>]*>', re.IGNORECASE), ''),
            (re.compile(r'<table[\s\S]*?</table>', re.IGNORECASE), ''),
            (re.compile(r'<script[\s\S]*?</script>', re.IGNORECASE), ''),
            (re.compile(r'<style[\s\S]*?</style>', re.IGNORECASE), ''),
        ]

    def generate(self, html_content: str, max_length: Optional[int] = None, 
                 preserve_formatting: Optional[bool] = None,
                 line_break_strategy: Optional[str] = None) -> str:
        """
        生成文章简介
        """
        if not html_content:
            return ""
        
        # 使用参数或默认值
        current_max_length = max_length if max_length is not None else self.max_length
        current_preserve_formatting = (
            preserve_formatting if preserve_formatting is not None 
            else self.preserve_formatting
        )
        current_strategy = (
            line_break_strategy if line_break_strategy is not None 
            else self.line_break_strategy
        )
        
        # 处理流程
        content = html.unescape(html_content)
        content = self._remove_complex_elements(content)
        
        if current_preserve_formatting:
            content = self._preserve_basic_formatting(content, current_strategy)
        else:
            content = self._remove_all_tags(content)
            content = self._handle_line_breaks(content, current_strategy)
            
        content = self._clean_whitespace(content, current_strategy)
        excerpt = self._smart_truncate(content, current_max_length)
        
        return excerpt

    def _preserve_basic_formatting(self, content: str, strategy: str) -> str:
        """保留基本文本格式并处理换行"""
        # 处理段落和换行
        if strategy == "preserve":
            # 保留所有换行结构
            content = re.sub(r'</p>\s*<p>', '\n\n', content)
            content = re.sub(r'<p[^>]*>', '', content)
            content = re.sub(r'</p>', '\n', content)
            content = re.sub(r'<br\s*/?>', '\n', content)
        elif strategy == "compact":
            # 所有换行转空格
            content = re.sub(r'</p>\s*<p>', ' ', content)
            content = re.sub(r'<p[^>]*>', '', content)
            content = re.sub(r'</p>', ' ', content)
            content = re.sub(r'<br\s*/?>', ' ', content)
        else:  # smart
            # 智能处理：段落间保留换行，行内换行转空格
            content = re.sub(r'</p>\s*<p>', '\n\n', content)
            content = re.sub(r'<p[^>]*>', '', content)
            content = re.sub(r'</p>', '\n', content)
            content = re.sub(r'<br\s*/?>', ' ', content)  # <br> 转空格
        
        # 处理其他格式
        content = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'**\1**', content)
        content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
        content = re.sub(r'<b>(.*?)</b>', r'**\1**', content)
        content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
        content = re.sub(r'<i>(.*?)</i>', r'*\1*', content)
        content = re.sub(r'<li>(.*?)</li>', r'• \1', content)
        
        # 最后移除所有剩余的HTML标签
        content = self._remove_all_tags(content)
        return content

    def _handle_line_breaks(self, content: str, strategy: str) -> str:
        """处理纯文本中的换行符"""
        if strategy == "preserve":
            # 保留原始换行
            return content
        elif strategy == "compact":
            # 所有换行转空格
            return re.sub(r'\s+', ' ', content)
        else:  # smart
            # 合并连续换行，保留段落分隔
            content = re.sub(r'\n\s*\n', '\n\n', content)
            # 单换行转空格
            content = re.sub(r'(?<!\n)\n(?!\n)', ' ', content)
            return content

    def _clean_whitespace(self, content: str, strategy: str) -> str:
        """清理空白字符"""
        if strategy == "preserve":
            # 保留换行，只清理其他空白
            content = re.sub(r'[^\S\n]+', ' ', content)  # 非换行空白转空格
        else:
            # 所有连续空白转单个空格
            content = re.sub(r'\s+', ' ', content)
        
        return content.strip()

    def _remove_complex_elements(self, content: str) -> str:
        """移除复杂HTML元素"""
        for pattern, replacement in self._complex_elements_patterns:
            content = pattern.sub(replacement, content)
        return content

    def _remove_all_tags(self, content: str) -> str:
        """移除所有HTML标签"""
        return re.sub(r'<[^>]+>', '', content)

    def _smart_truncate(self, text: str, max_length: int) -> str:
        """智能截断文本"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        
        # 查找合适的截断点
        truncate_points = []
        
        for ender in self.sentence_enders:
            pos = truncated.rfind(ender)
            if pos != -1:
                truncate_points.append(pos)
        
        for separator in self.word_separators:
            pos = truncated.rfind(separator)
            if pos != -1:
                truncate_points.append(pos)
        
        # 在换行处截断（如果使用preserve策略）
        if self.line_break_strategy == "preserve":
            line_break_pos = truncated.rfind('\n')
            if line_break_pos != -1:
                truncate_points.append(line_break_pos)
        
        if truncate_points:
            best_point = max(truncate_points)
            if best_point > max_length * 0.6:
                return truncated[:best_point + 1] + '...'
        
        return truncated + '...'



class MarkdownRenderer:
    def __init__(self, config: Dict, cache_data: Dict):
        """
        初始化构建器
        
        Args:
            config_path: config.yaml 文件路径
            cache_path: cache.json 文件路径
        """
        # self.config_path = config_path
        # self.cache_path = cache_path
        self.global_config = config
        self.partials = {}
        self.cache_data = cache_data
        self.cache_updates = {}  # 用于存储需要更新的cache数据
        
    def load_config(self) -> Dict[str, Any]:
        """加载全局配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.global_config = yaml.safe_load(f)
        return self.global_config
    
    def load_partials(self) -> Dict[str, str]:
        """加载部分模板文件"""
        partials_dir = self.global_config.get('partials_dir', 'partials')
        if not os.path.exists(partials_dir):
            return {}
            
        for file_path in Path(partials_dir).glob('*.mustache'):
            with open(file_path, 'r', encoding='utf-8') as f:
                template_name = file_path.stem
                self.partials[template_name] = f.read()
        
        return self.partials
    
    def load_cache(self) -> Dict[str, Any]:
        """加载缓存数据"""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                self.cache_data = json.load(f)
        return self.cache_data
    
    def update_cache(self) -> bool:
        """
        更新缓存数据中的description字段
        
        Returns:
            是否成功更新
        """
        try:
            # 更新cache_data中的description字段
            for md_file_path, updated_description in self.cache_updates.items():
                if md_file_path in self.cache_data:
                    self.cache_data[md_file_path]['description'] = updated_description
            
            print(f"✓ 已更新缓存数据中的 {len(self.cache_updates)} 个description字段")
            return True
            
        except Exception as e:
            print(f"✗ 更新缓存数据失败: {str(e)}")
            return False

    def save_cache(self) -> bool:
        """
        将更新后的缓存数据写回文件
        
        Returns:
            是否成功保存
        """
        try:
            # 写回文件
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 已保存缓存数据到文件")
            return True
            
        except Exception as e:
            print(f"✗ 保存cache.json失败: {str(e)}")
            return False
    
    def merge_configs(self, markdown_frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并全局配置和markdown头部信息
        
        Args:
            markdown_frontmatter: markdown文件的头部信息
            
        Returns:
            合并后的局部配置
        """
        # 创建全局配置的深拷贝，避免影响其他文件的处理
        local_config = self.global_config.copy()
        
        # 用markdown头部信息更新配置
        for key, value in markdown_frontmatter.items():
            local_config[key] = value
            
        return local_config
    
    def render_markdown_to_html(self, markdown_content: str, local_config: Dict[str, Any]) -> str:
        """
        将markdown内容渲染为HTML
        
        Args:
            markdown_content: markdown正文内容
            local_config: 局部配置
            
        Returns:
            渲染后的HTML
        """
        # 获取markdown扩展配置
        extensions = local_config.get('md_parser_extension', [])
        
        # 渲染markdown为HTML
        html_content = markdown.markdown(markdown_content, extensions=extensions)
        
        return html_content
    
    def extract_description1(self, html_content: str, max_length: int = 300) -> str:
        """
        从HTML内容中提取描述
        
        Args:
            html_content: HTML内容
            max_length: 最大长度
            
        Returns:
            提取的描述文本
        """
        # 移除HTML标签，获取纯文本
        text_content = re.sub(r'<[^>]+>', '', html_content)
        
        if len(text_content) <= max_length:
            return text_content
        
        # 如果超过最大长度，找到合适的位置截断
        truncated = text_content[:max_length]
        
        # 查找最后一个完整的句子结束位置
        sentence_end = max(
            truncated.rfind('。'),
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?'),
            truncated.rfind('；')
        )
        
        if sentence_end > max_length * 0.5:  # 确保截断位置不要太靠前
            return truncated[:sentence_end + 1]
        else:
            # 如果没有找到合适的句子结束位置，就在单词边界截断
            word_boundary = max(
                truncated.rfind(' '),
                truncated.rfind('，'),
                truncated.rfind(','),
                truncated.rfind('、')
            )
            if word_boundary > max_length * 0.5:
                return truncated[:word_boundary]
            else:
                return truncated
    
    def extract_description2(self, content, max_length=100):
        """
        智能截断HTML内容，保持标签完整性
        :param content: 原始HTML内容
        :param max_length: 最大字符数
        :return: 安全截断后的HTML内容
        """
        class HTMLTruncator(HTMLParser):
            def __init__(self):
                super().__init__()
                self.output = []
                self.stack = []
                self.total_len = 0
                self.truncated = False

            def handle_starttag(self, tag, attrs):
                if self.truncated:
                    return
                self.stack.append(tag)
                attrs_str = ''.join([f' {k}="{v}"' for k, v in attrs])
                self.output.append(f"<{tag}{attrs_str}>")

            def handle_endtag(self, tag):
                if self.truncated:
                    return
                if self.stack and self.stack[-1] == tag:
                    self.stack.pop()
                    self.output.append(f"</{tag}>")

            def handle_startendtag(self, tag, attrs):
                if self.truncated:
                    return
                attrs_str = ''.join([f' {k}="{v}"' for k, v in attrs])
                self.output.append(f"<{tag}{attrs_str}/>")

            def handle_data(self, data):
                if self.truncated:
                    return
                
                remaining = max_length - self.total_len
                if remaining <= 0:
                    self.truncated = True
                    return
                    
                if len(data) > remaining:
                    data = data[:remaining]
                    self.truncated = True
                    
                self.total_len += len(data)
                self.output.append(data)

        truncator = HTMLTruncator()
        truncator.feed(content)
        
        # 补全未闭合的标签
        while truncator.stack:
            tag = truncator.stack.pop()
            truncator.output.append(f"</{tag}>")
        
        # 添加省略提示
        if truncator.truncated:
            truncator.output.append("...")
        
        return ''.join(truncator.output)


    def extract_description(self, content, max_length=200):
        generator = SmartExcerptGenerator()
        ret = generator.generate(content, max_length)
        return ret


    def process_markdown_file(self, md_file_path: str) -> Optional[Dict[str, Any]]:
        """
        处理单个markdown文件
        
        Args:
            md_file_path: markdown文件路径
            
        Returns:
            处理结果信息
        """
        try:
            # 读取markdown文件
            with open(md_file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # 获取头部信息和正文内容
            frontmatter_data = post.metadata
            markdown_content = post.content
            
            # 合并配置
            local_config = self.merge_configs(frontmatter_data)
            
            # 渲染markdown为HTML
            html_content = self.render_markdown_to_html(markdown_content, local_config)
            
            # 提取描述
            description = self.extract_description(html_content)
            
            # 记录需要更新的description
            self.cache_updates[md_file_path] = description
            
            # 将渲染后的HTML作为部分模板
            self.partials['content'] = html_content
            
            # 准备模板渲染上下文
            template_context = local_config.copy()
            
            # 添加缓存中的信息到上下文（如果存在）
            if md_file_path in self.cache_data:
                cache_info = self.cache_data[md_file_path]
                template_context.update(cache_info)
            
            # 更新描述字段（用于模板渲染）
            template_context['description'] = description
            
            # 获取模板文件路径
            template_dir = local_config.get('template_dir', 'template')
            template_file = local_config.get('template', 'post.mustache')
            template_path = os.path.join(template_dir, template_file)
            
            # 渲染模板
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            final_html = chevron.render(template_content, template_context, partials_dict=self.partials)
            
            # 确定输出路径
            html_dir = local_config.get('html_dir', 'html')
            md_filename = Path(md_file_path).stem
            output_path = os.path.join(html_dir, f"{md_filename}.html")
            
            # 确保输出目录存在
            os.makedirs(html_dir, exist_ok=True)
            
            # 保存HTML文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            return {
                'success': True,
                'input_file': md_file_path,
                'output_file': output_path,
                'description': description,
                'local_config': local_config
            }
            
        except Exception as e:
            print(f"处理文件 {md_file_path} 时出错: {str(e)}")
            return {
                'success': False,
                'input_file': md_file_path,
                'error': str(e)
            }
    
    def run(self) -> List[Dict[str, Any]]:
        """
        构建所有需要构建的markdown文件
        
        Returns:
            构建结果列表
        """
        # 清空更新记录
        self.cache_updates = {}
        
        # 加载所有必要的数据
        # self.load_config()
        self.load_partials()
        # self.load_cache()
        
        results = []
        
        # 找出所有需要构建的文件
        files_to_build = []
        for md_file_path, cache_info in self.cache_data.items():
            if cache_info.get('should_build', False):
                files_to_build.append(md_file_path)
        
        print(f"找到 {len(files_to_build)} 个需要构建的文件")
        
        # 处理每个文件
        for md_file_path in files_to_build:
            if os.path.exists(md_file_path):
                result = self.process_markdown_file(md_file_path)
                results.append(result)
                
                if result['success']:
                    print(f"✓ 成功构建: {md_file_path} -> {result['output_file']}")
                else:
                    print(f"✗ 构建失败: {md_file_path} - {result['error']}")
            else:
                print(f"✗ 文件不存在: {md_file_path}")
                results.append({
                    'success': False,
                    'input_file': md_file_path,
                    'error': '文件不存在'
                })
        
        # 所有文件处理完成后，更新cache.json
        if self.cache_updates:
            self.update_cache()
        else:
            print("ℹ 没有需要更新的description字段")
        
        # 输出构建统计
        successful_builds = [r for r in results if r['success']]
        failed_builds = [r for r in results if not r['success']]
        
        print(f"\n构建完成!")
        print(f"成功: {len(successful_builds)} 个文件")
        print(f"失败: {len(failed_builds)} 个文件")

        return self.cache_data

# 使用示例
if __name__ == "__main__":
    # 初始化构建器
    builder = MarkdownRenderer("config.yaml", "cache.json")
    
    # 执行构建
    results = builder.run()
    
    