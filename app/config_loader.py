import os
import yaml
import json
import logging
from typing import Dict, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml", 
                 image_table_path: str = 'image_table.yaml',
                 cache_path: str = "cache.json"):
        self.config_path = config_path
        self.image_table_path = image_table_path
        self.cache_path = cache_path
        self.config = {}
        self.cache_data = {}
        self.force_rebuild_all = False

    def _get_file_mtime(self, file_path: str) -> float:
        """获取文件的修改时间，如果文件不存在返回0"""
        if os.path.exists(file_path):
            return os.path.getmtime(file_path)
        return 0.0

    def _get_dir_mtime(self, dir_path: str) -> float:
        """获取目录的最新修改时间（递归检查所有文件）"""
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return 0.0
        
        latest_mtime = 0.0
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_mtime = os.path.getmtime(file_path)
                if file_mtime > latest_mtime:
                    latest_mtime = file_mtime
        return latest_mtime

    def check_force_rebuild(self) -> bool:
        """
        检查是否需要强制重新构建所有内容
        规则：
        1. 如果 config.yaml 的修改时间比 cache.json 新
        2. 或者 partials_dir 的更新时间比 cache.json 新
        """
        cache_mtime = self._get_file_mtime(self.cache_path)
        
        # 检查 config.yaml
        config_mtime = self._get_file_mtime(self.config_path)
        if config_mtime > cache_mtime:
            logger.info("检测到 config.yaml 已更新，需要强制重新构建")
            return True
        
        # 检查 partials_dir
        partials_dir = self.config.get('partials_dir')
        if partials_dir:
            partials_mtime = self._get_dir_mtime(partials_dir)
            if partials_mtime > cache_mtime:
                logger.info("检测到 partials 目录已更新，需要强制重新构建")
                return True
        
        logger.info("无需强制重新构建")
        return False

    def load_config(self) -> Dict[str, Any]:
        """加载主配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"已加载配置文件: {self.config_path}")
            return self.config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    def load_image_table(self) -> Dict[str, Any]:
        """加载图片表"""
        try:
            if os.path.exists(self.image_table_path):
                with open(self.image_table_path, 'r', encoding='utf-8') as f:
                    image_table = yaml.safe_load(f) or {}
                self.config['image_table'] = image_table
                logger.info(f"已加载图片表: {self.image_table_path}")
            else:
                self.config['image_table'] = {}
                logger.warning(f"图片表文件不存在: {self.image_table_path}")
            return self.config['image_table']
        except Exception as e:
            logger.error(f"加载图片表失败: {e}")
            raise

    def load_partials(self) -> Dict[str, str]:
        """加载 partials 目录中的所有 mustache 文件"""
        partials = {}
        
        # 检查是否配置了 partials_dir
        partials_dir = self.config.get('partials_dir')
        if not partials_dir:
            logger.warning("未配置 partials_dir，跳过加载 partials")
            return partials
        
        if not os.path.exists(partials_dir):
            logger.warning(f"partials 目录不存在: {partials_dir}")
            return partials
        
        try:
            # 遍历 partials 目录中的所有 .mustache 文件
            for filename in os.listdir(partials_dir):
                if filename.endswith('.mustache'):
                    file_path = os.path.join(partials_dir, filename)
                    if os.path.isfile(file_path):
                        # 读取文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 使用文件名（不含扩展名）作为 partial 名称
                        partial_name = os.path.splitext(filename)[0]
                        partials[partial_name] = content
                        logger.debug(f"已加载 partial: {partial_name}")
            
            self.config['partials'] = partials
            logger.info(f"已从 {partials_dir} 加载 {len(partials)} 个 partials")
            return partials
            
        except Exception as e:
            logger.error(f"加载 partials 失败: {e}")
            raise

    def load_cache(self) -> Dict[str, Any]:
        """加载缓存数据"""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
                logger.info(f"已加载缓存，共 {len(self.cache_data)} 条记录")
            else:
                self.cache_data = {}
                logger.info("缓存文件不存在，创建空缓存")
            return self.cache_data
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            raise

    def save_cache(self) -> None:
        """保存缓存数据"""
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存缓存到: {self.cache_path}")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
            raise

    def run(self) -> Tuple[Dict[str, Any], Dict[str, Any], bool]:
        """
        执行完整的配置加载流程
        返回: (config, cache_data, force_rebuild_all)
        """
        try:
            # 首先加载配置（不包含 partials）
            self.load_config()
            self.load_image_table()
            
            # 检查是否需要强制重新构建
            self.force_rebuild_all = self.check_force_rebuild()
            
            # 加载缓存和 partials
            self.load_cache()
            self.load_partials()
            
            logger.info(f"force_rebuild_all: {self.force_rebuild_all}")
            return self.config, self.cache_data, self.force_rebuild_all
            
        except Exception as e:
            logger.error(f"配置加载流程失败: {e}")
            raise