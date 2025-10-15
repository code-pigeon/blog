import os
import yaml
import json
import logging
from DependencyChecker import DependencyChecker
from MarkdownRenderer import MarkdownRenderer
from ext_timeline import TimelineGenerator
from ext_category import CategoryGenerator
from ext_feed import generate_feed


config_path = "config.yaml"
cache_path = "cache.json"

try:

	checker = DependencyChecker(config_path, cache_path)
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
