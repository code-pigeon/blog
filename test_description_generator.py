import re
import html
from typing import Optional, List

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
        # 先处理段落结构
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
            # 智能处理：段落间保留双换行，行内换行转空格
            content = re.sub(r'</p>\s*<p>', '\n\n', content)  # 段落间双换行
            content = re.sub(r'<p[^>]*>', '', content)
            content = re.sub(r'</p>', '\n\n', content)  # 段落结束双换行
            content = re.sub(r'<br\s*/?>', ' ', content)  # 行内换行转空格
        
        # 处理其他格式
        content = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'**\1**', content)
        content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
        content = re.sub(r'<b>(.*?)</b>', r'**\1**', content)
        content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
        content = re.sub(r'<i>(.*?)</i>', r'*\1*', content)
        content = re.sub(r'<li>(.*?)</li>', r'• \1', content)
        
        # 最后移除所有剩余的HTML标签
        content = self._remove_all_tags(content)
        
        # 对smart策略进行额外的空白清理（但保留双换行）
        if strategy == "smart":
            content = self._clean_smart_whitespace(content)
        
        return content

    def _clean_smart_whitespace(self, content: str) -> str:
        """智能清理空白，保留段落分隔"""
        # 保留双换行，清理其他空白
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 清理每行内的多余空白
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            if cleaned_line:  # 只保留非空行
                cleaned_lines.append(cleaned_line)
        
        # 用双换行重新连接，模拟段落结构
        return '\n\n'.join(cleaned_lines)

    def _handle_line_breaks(self, content: str, strategy: str) -> str:
        """处理纯文本中的换行符"""
        if strategy == "preserve":
            return content
        elif strategy == "compact":
            return re.sub(r'\s+', ' ', content)
        else:  # smart
            # 对于smart策略，如果内容中还有换行，说明是来自其他处理
            # 这里主要处理原始的纯文本换行
            lines = content.split('\n')
            if len(lines) <= 1:
                # 没有换行，直接返回
                return re.sub(r'\s+', ' ', content)
            else:
                # 有换行，进行智能处理
                return self._clean_smart_whitespace(content)

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

# 测试不同换行策略
def test_line_break_strategies():
    """测试不同换行处理策略"""
    
    test_html = """
    <p>这是第一个段落。</p>
    <p>这是第二个段落，<br>中间有换行符。</p>
    
    <p>这是第三个段落。</p>
    """
    
    generator = SmartExcerptGenerator(max_length=150)
    
    print("=== 不同换行处理策略对比 ===\n")
    
    strategies = ["smart", "preserve", "compact"]
    
    for strategy in strategies:
        print(f"策略: {strategy}")
        result = generator.generate(test_html, line_break_strategy=strategy)
        print(f"结果: {repr(result)}")
        print("-" * 50)

if __name__ == "__main__":
    test_line_break_strategies()