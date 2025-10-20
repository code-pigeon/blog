import os
import yaml
import json
import logging
from app.dependency_checker import DependencyChecker
from app.markdown_renderer import MarkdownRenderer
from app.ext_timeline import TimelineGenerator
from app.ext_category import CategoryGenerator
from app.ext_feed import generate_feed


config_path = "config.yaml"
image_table_path = 'image_table.yaml'
cache_path = "cache.json"

try:
	with open(config_path, 'r', encoding='utf-8') as f:
		config = yaml.safe_load(f)

	with open(image_table_path, 'r', encoding='utf-8') as f:
		config['image_table'] = yaml.safe_load(f)

	with open(cache_path, 'r', encoding='utf-8') as f:
		cache_data = json.load(f)

	print(f"已加载缓存，共 {len(cache_data)} 条记录")

	checker = DependencyChecker(config, cache_data, config_path, cache_path)
	config, cache_data = checker.run()

	renderer = MarkdownRenderer(config, cache_data)
	cache_data = renderer.run()


	# --- 扩展 ------------------------------------------------

	generate_feed(config, cache_data)

	generator = TimelineGenerator(config, cache_data)
	generator.run()
	generator = CategoryGenerator(config, cache_data)
	generator.run()

	with open(cache_path, 'w', encoding='utf-8') as f:
		json.dump(cache_data, f, ensure_ascii=False, indent=2)

except Exception as e:
    logger.error(f"程序执行失败: {e}")



# print(config)
# print("++++++++++++++++++++++++++++++")
# print(cache_data)
