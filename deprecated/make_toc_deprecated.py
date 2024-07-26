#!/usr/bin/python3

from pathlib import Path
import sys
import os

import datetime
from dateutil.relativedelta import relativedelta


# def get_modified_time_str(path):
# 	# 参数为Path对象
# 	mtime_timestamp = path.stat().st_mtime
# 	mtime_datetime = datetime.datetime.fromtimestamp(mtime_timestamp)
# 	mtime_formatted = mtime_datetime.strftime('%Y-%m-%d %H:%M')
# 	return mtime_formatted


# # 定义一个函数，用来获取对象的修改时间
# def get_modified_time(path_obj):
#     return path_obj.stat().st_mtime


# if len(sys.argv) != 2:
# 	print("Usage: python3 make_toc.py path_name", file=sys.stderr)
# 	exit(-1)
# directory = sys.argv[1]
# path = Path(directory)

# def ls_by_category(path, depth):
# 	try:
# 		items = list(path.iterdir())
# 		items = sorted(items)
# 		for p in items:
# 			# print("执行到这里了")
# 			if p.is_dir():
# 				text = "#" * depth + ' ' + p.stem
# 				print(text)
# 				ls_by_category(p, depth + 1)
# 			elif depth > 2:
# 				# print("执行到这里了")
# 				if not str(p.stem).startswith('IGNORE_'):  # 以IGNORE_开头的不要放入目录
# 					text = f"\n[{p.stem}]({p.stem}.html)\n"
# 					print(text)
# 	except Exception as e:
# 		print(e)


# def sort_path_by_date(path):
# 	contents = []
# 	def iter_path(path):
# 		for p in path.iterdir():
# 			if p.is_dir():
# 				iter_path(p)
# 			else:
# 				contents.append(p)
# 	iter_path(path)
# 	print(contents)
# 	sorted(contents, key=lambda x:get_modified_time(x), reverse=True)
# 	print(contents)
# 	return contents

# contents = sort_path_by_date(path)



# for i in contents:
	# print(i.stem)
	# print(get_modified_time_str(i))
	# print(get_modified_time(i))
	# if get_modified_time(i) > 


# ls_by_date(path)

# ls_by_category(path, 2)
# exit(0)

# md_sorted_by_date = {}

# items = list(path.iterdir())

# print(items)

# for p in items:
# 	print(p.stem)

# ---- 旧版 ---------------------------------------------------------------

def ls(path, depth):
	try:
		items = list(path.iterdir())
		items = sorted(items)
		for p in items:
			# print("执行到这里了")
			if p.is_dir():
				text = "#" * depth + ' ' + p.stem
				print(text)
				ls(p, depth + 1)
			elif depth != 2:
				# print("执行到这里了")
				if not str(p.stem).startswith('IGNORE_'):  # 以IGNORE_开头的不要放入目录
					text = f"\n[{p.stem}]({p.relative_to(directory)})\n"
					print(text)
	except Exception as e:
		print(e)

