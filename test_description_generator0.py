import re
import html
from typing import Optional, List

class SmartExcerptGenerator:
    """
    智能文章简介生成器
    
    用于从HTML内容中生成格式良好的文章简介，支持智能截断和格式保留
    """
    
    def __init__(self, max_length: int = 200, preserve_formatting: bool = True):
        """
        初始化生成器
        
        Args:
            max_length: 简介最大长度
            preserve_formatting: 是否保留基本格式
        """
        self.max_length = max_length
        self.preserve_formatting = preserve_formatting
        
        # 配置参数
        self.sentence_enders = ['。', '！', '？', '.', '!', '?']
        self.word_separators = ['，', ',', ' ']
        
        # 编译正则表达式以提高性能
        self._complex_elements_patterns = [
            (re.compile(r'<pre>[\s\S]*?</pre>', re.IGNORECASE), ''),
            (re.compile(r'<code>[\s\S]*?</code>', re.IGNORECASE), ''),
            (re.compile(r'<img[^>]*>', re.IGNORECASE), ''),
            (re.compile(r'<table[\s\S]*?</table>', re.IGNORECASE), ''),
            (re.compile(r'<script[\s\S]*?</script>', re.IGNORECASE), ''),
            (re.compile(r'<style[\s\S]*?</style>', re.IGNORECASE), ''),
        ]
        
        self._formatting_patterns = [
            (re.compile(r'<h[1-6][^>]*>(.*?)</h[1-6]>', re.IGNORECASE), r'**\1**'),
            (re.compile(r'<strong>(.*?)</strong>', re.IGNORECASE), r'**\1**'),
            (re.compile(r'<b>(.*?)</b>', re.IGNORECASE), r'**\1**'),
            (re.compile(r'<em>(.*?)</em>', re.IGNORECASE), r'*\1*'),
            (re.compile(r'<i>(.*?)</i>', re.IGNORECASE), r'*\1*'),
            (re.compile(r'<li>(.*?)</li>', re.IGNORECASE), r'• \1'),
            (re.compile(r'</p>\s*<p>', re.IGNORECASE), '\n\n'),
            (re.compile(r'<p[^>]*>', re.IGNORECASE), ''),
            (re.compile(r'</p>', re.IGNORECASE), '\n'),
            (re.compile(r'<br\s*/?>', re.IGNORECASE), '\n'),
        ]
    
    def generate(self, html_content: str, max_length: Optional[int] = None, 
                 preserve_formatting: Optional[bool] = None) -> str:
        """
        生成文章简介
        
        Args:
            html_content: HTML内容
            max_length: 最大长度（如为None则使用初始化设置）
            preserve_formatting: 是否保留格式（如为None则使用初始化设置）
            
        Returns:
            处理后的简介文本
        """
        if not html_content:
            return ""
        
        # 使用参数或默认值
        current_max_length = max_length if max_length is not None else self.max_length
        current_preserve_formatting = (
            preserve_formatting if preserve_formatting is not None 
            else self.preserve_formatting
        )
        
        # 处理流程
        content = html.unescape(html_content)
        content = self._remove_complex_elements(content)
        
        if current_preserve_formatting:
            content = self._preserve_basic_formatting(content)
        else:
            content = self._remove_all_tags(content)
            
        content = self._clean_whitespace(content)
        excerpt = self._smart_truncate(content, current_max_length)
        
        return excerpt
    
    def _remove_complex_elements(self, content: str) -> str:
        """移除复杂HTML元素"""
        for pattern, replacement in self._complex_elements_patterns:
            content = pattern.sub(replacement, content)
        return content
    
    def _preserve_basic_formatting(self, content: str) -> str:
        """保留基本文本格式"""
        for pattern, replacement in self._formatting_patterns:
            content = pattern.sub(replacement, content)
        
        # 最后移除所有剩余的HTML标签
        content = self._remove_all_tags(content)
        return content
    
    def _remove_all_tags(self, content: str) -> str:
        """移除所有HTML标签"""
        return re.sub(r'<[^>]+>', '', content)
    
    def _clean_whitespace(self, content: str) -> str:
        """清理空白字符"""
        content = re.sub(r'\s+', ' ', content)
        return content.strip()
    
    def _smart_truncate(self, text: str, max_length: int) -> str:
        """智能截断文本"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        
        # 查找合适的截断点
        truncate_points = []
        
        # 句子结束符
        for ender in self.sentence_enders:
            pos = truncated.rfind(ender)
            if pos != -1:
                truncate_points.append(pos)
        
        # 词语分隔符
        for separator in self.word_separators:
            pos = truncated.rfind(separator)
            if pos != -1:
                truncate_points.append(pos)
        
        # 找到最后一个合适的截断点
        if truncate_points:
            best_point = max(truncate_points)
            if best_point > max_length * 0.6:  # 确保不会截断太多
                return truncated[:best_point + 1] + '...'
        
        # 如果没有找到合适的截断点
        return truncated + '...'
    
    def batch_generate(self, html_contents: List[str], **kwargs) -> List[str]:
        """
        批量生成简介
        
        Args:
            html_contents: HTML内容列表
            **kwargs: 传递给generate方法的参数
            
        Returns:
            简介列表
        """
        return [self.generate(content, **kwargs) for content in html_contents]
    
    def update_config(self, max_length: Optional[int] = None, 
                     preserve_formatting: Optional[bool] = None,
                     sentence_enders: Optional[List[str]] = None,
                     word_separators: Optional[List[str]] = None):
        """更新配置参数"""
        if max_length is not None:
            self.max_length = max_length
        if preserve_formatting is not None:
            self.preserve_formatting = preserve_formatting
        if sentence_enders is not None:
            self.sentence_enders = sentence_enders
        if word_separators is not None:
            self.word_separators = word_separators
    
    def get_config(self) -> dict:
        """获取当前配置"""
        return {
            'max_length': self.max_length,
            'preserve_formatting': self.preserve_formatting,
            'sentence_enders': self.sentence_enders,
            'word_separators': self.word_separators
        }


# 使用示例和测试
def demo():
    """演示使用方法"""
    
    # 测试数据
    test_html = """
    <h1>《双开行动》——刘学文</h1>
    <br>
    <p>于2023/06/01读完，评语“有点狗血”</p>
    
    <strong>个人评价</strong>
    <p>评分：<b>★★★☆☆</b></p>
    
    <p>确实还是差点意思，主角毋庸置疑的好人，反派是毋庸置疑的反派。剧里的反派女角色行为出奇的一致，都是在名利场里傻傻地相信着真爱，而正派的女角色行为同样出其的一致，都喜欢动不动就留信出家。</p>
    
    <em>书摘</em>
    <ul>
        <li>可心</li>
        <li>伉俪</li>
        <li>下野</li>
    </ul>
    
    <p>那天我知道了你就是那年给我输过血的女知青的时候，我就对你充满了一种天然的信任，和你在一起，让我感觉到踏实。</p>
    """
    
    # 创建生成器实例
    generator = SmartExcerptGenerator()
    
    print("默认配置生成:")
    print(generator.generate(test_html))
    print("\n" + "="*60 + "\n")
    
    # 自定义参数生成
    print("自定义长度(100)生成:")
    print(generator.generate(test_html, max_length=100))
    print("\n" + "="*60 + "\n")
    
    # 不保留格式生成
    print("不保留格式生成:")
    print(generator.generate(test_html, preserve_formatting=False))
    print("\n" + "="*60 + "\n")
    
    # 批量生成示例
    multiple_contents = [test_html, "<p>另一篇短文测试</p>", "<h2>标题</h2><p>内容</p>"]
    print("批量生成:")
    results = generator.batch_generate(multiple_contents, max_length=50)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result}")
    
    print("\n" + "="*60 + "\n")
    
    # 配置管理演示
    print("当前配置:")
    print(generator.get_config())
    
    # 更新配置
    generator.update_config(max_length=150, preserve_formatting=False)
    print("\n更新后配置:")
    print(generator.get_config())
    print("\n使用新配置生成:")
    print(generator.generate(test_html))


if __name__ == "__main__":
    demo()