import os
import logging
from app.config_loader import ConfigLoader
from app.dependency_checker import DependencyChecker
from app.markdown_renderer import MarkdownRenderer
from app.ext_timeline import TimelineGenerator
from app.ext_category import CategoryGenerator
from app.ext_feed import generate_feed
from app.ext_shuoshuo import ShuoshuoGenerator  # 新增导入

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # 使用 ConfigLoader 加载配置
    config_loader = ConfigLoader(
        config_path="config.yaml",
        image_table_path='image_table.yaml',
        cache_path="cache.json"
    )
    config, cache_data, force_rebuild_all = config_loader.run()

    # 检查依赖，传递 force_rebuild_all 参数
    checker = DependencyChecker(config, cache_data, "config.yaml", "cache.json")
    config, cache_data = checker.run(force_rebuild_all=force_rebuild_all)

    # 渲染 Markdown，传递 force_rebuild_all 参数
    renderer = MarkdownRenderer(config, cache_data)
    cache_data = renderer.run()

    # --- 扩展功能 ------------------------------------------------
    generate_feed(config, cache_data)

    generator = TimelineGenerator(config, cache_data)
    generator.run()
    
    generator = CategoryGenerator(config, cache_data)
    generator.run()

    # 新增：生成说说页面
    generator = ShuoshuoGenerator(config)
    generator.run()


    # 保存缓存
    config_loader.cache_data = cache_data
    config_loader.save_cache()

    logger.info("程序执行完成")

except Exception as e:
    logger.error(f"程序执行失败: {e}")
    raise