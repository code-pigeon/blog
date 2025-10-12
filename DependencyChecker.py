import os
import json
import yaml
import frontmatter
from datetime import datetime
from urllib.parse import quote
from pathlib import Path


class DependencyChecker:
    def __init__(self, config_path, md_dir_path, html_dir_path, cache_path):
        """
        初始化依赖检查模块
        
        Args:
            config_path: config.yaml文件路径
            md_dir_path: markdown文件夹路径
            html_dir_path: html文件夹路径
            cache_path: cache文件路径
        """
        self.config_path = self.normalize_path(config_path)
        self.md_dir_path = self.normalize_path(md_dir_path)
        self.html_dir_path = self.normalize_path(html_dir_path)
        self.cache_path = self.normalize_path(cache_path)
        
        # 加载配置
        self.config = self.load_config()
        
        # 缓存数据
        self.cache_data = {}
        
        # 确保路径都是绝对路径
        self.md_dir_path = self.ensure_absolute_path(self.md_dir_path)
        self.html_dir_path = self.ensure_absolute_path(self.html_dir_path)
        self.blog_root = Path(self.md_dir_path).parent
        
        # 记录配置文件的修改时间戳
        self.config_timestamp = self.get_file_timestamp(self.config_path)

    def normalize_path(self, path):
        """将路径转换为Linux风格"""
        return str(Path(path)).replace('\\', '/')

    def ensure_absolute_path(self, path):
        """确保路径是绝对路径"""
        path_obj = Path(path)
        if not path_obj.is_absolute():
            # 如果路径是相对的，基于当前工作目录转换为绝对路径
            path_obj = Path.cwd() / path_obj
        return self.normalize_path(path_obj)

    def load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def load_cache(self):
        """加载缓存文件，如果不存在则创建空缓存"""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                self.cache_data = json.load(f)
        else:
            self.cache_data = {}

    def save_cache(self):
        """保存缓存文件"""
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.cache_data, f, ensure_ascii=False, indent=2)

    def get_file_timestamp(self, file_path):
        """获取文件的修改时间戳"""
        return os.path.getmtime(file_path)

    def timestamp_to_readable(self, timestamp):
        """将时间戳转换为可读格式（用于显示）"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%y/%m/%d/%H:%M")

    def get_cache_timestamp(self):
        """获取缓存文件的修改时间戳，如果文件不存在返回None"""
        if os.path.exists(self.cache_path):
            return self.get_file_timestamp(self.cache_path)
        return None

    def should_force_rebuild_all(self):
        """
        判断是否需要强制重建所有markdown文件
        规则：如果cache文件的修改日期比config的修改日期要小，那么所有md的should_build都为true
        
        Returns:
            bool: 是否需要强制重建所有文件
        """
        cache_timestamp = self.get_cache_timestamp()
        
        if cache_timestamp is None:
            # 如果缓存文件不存在，不需要强制重建（因为所有文件都会被认为是新的）
            return False
        
        # 直接比较时间戳
        if cache_timestamp < self.config_timestamp:
            config_time_str = self.timestamp_to_readable(self.config_timestamp)
            cache_time_str = self.timestamp_to_readable(cache_timestamp)
            print(f"配置文件已更新，强制重建所有markdown文件")
            print(f"  配置文件修改时间: {config_time_str}")
            print(f"  缓存文件修改时间: {cache_time_str}")
            return True
                
        return False

    def get_all_markdown_files(self):
        """获取所有markdown文件的绝对路径（Linux风格），忽略以NOCHECK_开头的文件"""
        md_files = []
        md_dir = Path(self.md_dir_path)
        
        for file_path in md_dir.rglob("*.md"):
            # 跳过以NOCHECK_开头的文件
            if file_path.stem.startswith("NOCHECK_"):
                continue
            md_files.append(self.normalize_path(file_path.absolute()))
        
        return md_files

    def get_all_html_files(self):
        """获取所有html文件的绝对路径（Linux风格），忽略以NOCHECK_开头的文件"""
        html_files = []
        html_dir = Path(self.html_dir_path)
        
        for file_path in html_dir.glob("*.html"):
            # 跳过以NOCHECK_开头的文件
            if file_path.stem.startswith("NOCHECK_"):
                continue
            html_files.append(self.normalize_path(file_path.absolute()))
        
        return html_files


    def get_category_from_path(self, md_file_path):
        """
        从文件路径中提取分类信息
        
        Args:
            md_file_path: markdown文件的绝对路径（Linux风格）
            
        Returns:
            list: 分类列表，如["瞎聊", "二级分类"]
        """
        md_dir = Path(self.md_dir_path)
        file_path = Path(md_file_path)
        
        # 获取相对于md_dir的相对路径
        try:
            relative_path = file_path.relative_to(md_dir)
        except ValueError:
            # 如果路径不在md_dir下，返回空分类
            print(f"警告: 文件 {md_file_path} 不在markdown目录 {self.md_dir_path} 下")
            return []
        
        # 获取父目录部分（排除文件名）
        parent_dirs = relative_path.parent.parts
        
        # 过滤掉空字符串和当前目录标记
        category = [dir_name for dir_name in parent_dirs if dir_name not in ['.', '']]
        
        return category

    def get_html_filename(self, md_file_path):
        """
        根据markdown文件路径生成对应的html文件名
        
        Args:
            md_file_path: markdown文件的绝对路径（Linux风格）
            
        Returns:
            str: html文件名
        """
        md_file = Path(md_file_path)
        # 获取文件名（不含路径），并将扩展名改为.html
        html_filename = md_file.stem + ".html"
        return html_filename

    def get_html_file_path(self, md_file_path):
        """
        获取markdown文件对应的html文件路径（Linux风格）
        
        Args:
            md_file_path: markdown文件的绝对路径（Linux风格）
            
        Returns:
            str: html文件的绝对路径（Linux风格）
        """
        html_filename = self.get_html_filename(md_file_path)
        html_dir = Path(self.html_dir_path)
        return self.normalize_path(html_dir / html_filename)

    def generate_link(self, md_file_path):
        """
        生成link和quote_link
        
        Args:
            md_file_path: markdown文件的绝对路径（Linux风格）
            
        Returns:
            tuple: (link, quote_link)
        """
        html_filename = self.get_html_filename(md_file_path)
        
        # 获取相对于博客根目录的html文件路径
        html_relative_path = Path(self.config['html_dir']) / html_filename
        html_relative_str = self.normalize_path(html_relative_path)
        
        # 生成link
        site = self.config['site'].rstrip('/')
        link = f"{site}/{html_relative_str}"
        
        # 生成quote_link（对特殊字符进行编码）
        quote_link = quote(link, safe=':/')
        
        return link, quote_link

    def should_build_markdown(self, md_file_path, html_file_path, current_timestamp, force_rebuild_all=False):
        """
        判断是否需要构建markdown文件
        
        Args:
            md_file_path: markdown文件路径（Linux风格）
            html_file_path: 对应的html文件路径（Linux风格）
            current_timestamp: 当前markdown文件的修改时间戳
            force_rebuild_all: 是否强制重建所有文件
            
        Returns:
            bool: 是否需要构建
        """
        # 如果强制重建所有文件，直接返回true
        if force_rebuild_all:
            return True
            
        md_file_str = self.normalize_path(md_file_path)
        
        # 规则1: 如果cache中找不到对应的markdown文件，则新增记录，should_build为true
        if md_file_str not in self.cache_data:
            return True
        
        cache_entry = self.cache_data[md_file_str]
        
        # 规则2: 如果cache中找到对应的markdown文件，但无对应html，should_build为true
        if not os.path.exists(html_file_path):
            return True
        
        # 规则3: 如果markdown的文件修改时间大于cache中记录的file_updated，should_build为true
        cache_timestamp = cache_entry.get('file_updated', 0)  # 默认值为0，确保新文件会被构建
        
        # 直接比较时间戳
        if current_timestamp > cache_timestamp:
            return True
        
        # 规则4: 如果markdown的文件修改时间小于cache中记录的file_updated，should_build为false
        return False

    def parse_markdown_frontmatter(self, md_file_path):
        """
        解析markdown文件的frontmatter
        
        Args:
            md_file_path: markdown文件路径（Linux风格）
            
        Returns:
            dict: frontmatter数据
        """
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                
            frontmatter_data = {}
            frontmatter_data['title'] = post.get('title', '')
            frontmatter_data['date'] = post.get('date', '')
            frontmatter_data['updated'] = post.get('updated', None)
            
            return frontmatter_data
            
        except Exception as e:
            print(f"解析markdown文件frontmatter失败: {md_file_path}, 错误: {e}")
            return {
                'title': '',
                'date': '',
                'updated': None
            }

    def clean_orphaned_html_files(self):
        """清理孤立的html文件（有html但没有对应的markdown），忽略以NOCHECK_开头的文件"""
        all_md_files = self.get_all_markdown_files()
        all_html_files = self.get_all_html_files()
        
        # 构建markdown文件对应的html文件路径集合
        md_html_paths = {self.get_html_file_path(md_file) for md_file in all_md_files}
        
        # 找出孤立的html文件（不包括NOCHECK_开头的文件）
        orphaned_html_files = [html_file for html_file in all_html_files 
                              if html_file not in md_html_paths]
        
        # 删除孤立的html文件
        for html_file in orphaned_html_files:
            try:
                os.remove(html_file)
                print(f"已删除孤立的html文件: {html_file}")
            except Exception as e:
                print(f"删除html文件失败: {html_file}, 错误: {e}")

    def process_markdown_files(self):
        """处理所有markdown文件，更新缓存"""
        all_md_files = self.get_all_markdown_files()
        
        print(f"找到 {len(all_md_files)} 个markdown文件")
        
        # 检查是否需要强制重建所有文件
        force_rebuild_all = self.should_force_rebuild_all()
        
        # 清理缓存中不存在的文件
        cache_keys_to_remove = []
        for cached_file_path in self.cache_data.keys():
            if cached_file_path not in all_md_files:
                cache_keys_to_remove.append(cached_file_path)
        
        # 删除不存在的文件记录
        for key in cache_keys_to_remove:
            del self.cache_data[key]
            print(f"已删除缓存中不存在的文件记录: {key}")
        
        if cache_keys_to_remove:
            print(f"共删除 {len(cache_keys_to_remove)} 条不存在的文件记录")
        
        for md_file_path in all_md_files:
            print(f"处理文件: {md_file_path}")
            
            current_timestamp = self.get_file_timestamp(md_file_path)
            html_file_path = self.get_html_file_path(md_file_path)
            
            should_build = self.should_build_markdown(
                md_file_path, html_file_path, current_timestamp, force_rebuild_all
            )
            
            # 如果需要构建或者缓存中没有该文件，则更新缓存
            if should_build or self.normalize_path(md_file_path) not in self.cache_data:
                # 解析frontmatter
                frontmatter_data = self.parse_markdown_frontmatter(md_file_path)
                
                # 获取分类信息
                category = self.get_category_from_path(md_file_path)
                
                # 生成链接
                link, quote_link = self.generate_link(md_file_path)
                
                # 更新缓存，存储时间戳
                self.cache_data[self.normalize_path(md_file_path)] = {
                    "file_updated": current_timestamp,  # 存储时间戳而不是格式化字符串
                    "should_build": should_build,
                    "title": frontmatter_data['title'],
                    "category": category,
                    "date": frontmatter_data['date'],
                    "updated": frontmatter_data['updated'],
                    "link": link,
                    "quote_link": quote_link,
                    "description": ""  # 暂不处理description字段
                }
                
                build_reason = "强制重建所有文件" if force_rebuild_all else "文件已更新"
                readable_time = self.timestamp_to_readable(current_timestamp)
                print(f"  - 需要构建: {should_build}, 原因: {build_reason}, 分类: {category}, 修改时间: {readable_time}")
            else:
                # 如果不需要构建，只更新should_build字段
                self.cache_data[self.normalize_path(md_file_path)]['should_build'] = False
                print(f"  - 不需要构建")

    def run(self):
        """运行依赖检查"""
        print("开始依赖检查...")
        print(f"Markdown目录: {self.md_dir_path}")
        print(f"HTML目录: {self.html_dir_path}")
        print(f"缓存文件: {self.cache_path}")
        config_time_str = self.timestamp_to_readable(self.config_timestamp)
        print(f"配置文件: {self.config_path} (修改时间: {config_time_str})")
        
        # 加载缓存
        self.load_cache()
        print(f"已加载缓存，共 {len(self.cache_data)} 条记录")
        
        # 清理孤立的html文件
        print("检查孤立的html文件...")
        self.clean_orphaned_html_files()
        
        # 处理所有markdown文件
        print("处理markdown文件...")
        self.process_markdown_files()
        
        # 保存缓存
        self.save_cache()
        print(f"缓存已保存，共 {len(self.cache_data)} 条记录")
        
        # 统计需要构建的文件数量
        build_count = sum(1 for entry in self.cache_data.values() if entry['should_build'])
        print(f"需要构建的文件数量: {build_count}")
        
        return self.cache_data


def main():
    """主函数，用于测试"""
    # 这里需要替换为实际的路径
    config_path = "config.yaml"
    md_dir_path = "md"
    html_dir_path = "html"
    cache_path = "cache.json"
    
    checker = DependencyChecker(config_path, md_dir_path, html_dir_path, cache_path)
    cache_data = checker.run()
    
    # 打印需要构建的文件
    print("\n需要构建的文件:")
    for file_path, data in cache_data.items():
        if data['should_build']:
            readable_time = checker.timestamp_to_readable(data['file_updated'])
            print(f"- {file_path} (修改时间: {readable_time})")

if __name__ == "__main__":
    main()