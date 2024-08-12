#!/usr/bin/python3

import sys 
import os
import datetime
from dateutil.relativedelta import relativedelta

def make_toc_by_category(path, output_file=sys.stdout, prefix='##'):
	"""
	制作以类别分类的目录
	:param path: 要遍历的路径。
	:param prefix: 当前缩进前缀。
	:param output_file: 保存打印内容的文件，默认为stdout
	"""
	files = sorted(os.listdir(path))  # 按字典顺序sorted一下
	for file in files:
		new_path = os.path.join(path, file)
		if os.path.isdir(new_path):
		# --- 跳过图片区了 --------------------
			if file == '图片区':
				continue
		# -----------------------------------
			new_prefix = prefix + '#'
			print(prefix + ' ' + file, file=output_file)
			make_toc_by_category(new_path, output_file, new_prefix)
		else:
			if (file.startswith('IGNORE_')):
				# 跳过以"IGNORE_"开头的文件
				continue

			if (file.startswith('时间轴') or file.startswith('分类')):
				# 跳过自己
				continue;

			file_stem = file[:file.rfind('.')]
			file_html_link = f"[{file_stem}]({file_stem + '.html'})"
			print("- " + datetime.datetime.fromtimestamp(os.path.getmtime(new_path)).strftime('%Y.%m.%d') +
				"："  + file_html_link, 
				file=output_file)


def make_toc_by_mtime(path, output_file=sys.stdout):

	prefix_year = "## "
	prefix_month = "### "

	# 存储所有文件的路径和修改时间
	all_files_with_mtime = []

	# 遍历文件夹
	for dirpath, dirnames, filenames in os.walk(path):
		for filename in filenames:
			# 获取文件的完整路径
			file_path = os.path.join(dirpath, filename)
			# 获取文件的修改时间
			modification_time = os.path.getmtime(file_path)
			# 将文件路径和修改时间作为一个元组添加到列表中
			all_files_with_mtime.append((file_path, modification_time))

	all_files_with_mtime.sort(key=lambda x: x[1], reverse=True)

	if len(all_files_with_mtime) == 0:
		# 虽然这个错误不太可能发生
		print(f"{sys.argv[0]}: \033[31m[Error]\033[0m \
			there is not file in \"{path}\"", file=sys.stderr)
		exit(1)

	# time_for_compare 为了输出“年/月”标题而存在
	time_for_compare = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + relativedelta(years=1)
	
	for item in all_files_with_mtime:
		file_name = os.path.basename(item[0])

	# ---- 跳过的文件 -----------------------------------------------
		if (file_name.startswith('IGNORE_')):
			# 跳过以"IGNORE_"开头的文件
			continue
		if (file_name.startswith('收集')):
			# 跳过以"IGNORE_"开头的文件
			continue
		if (file_name.startswith('时间轴') or file_name.startswith('分类')):
			# 跳过自己
			continue;
	# --------------------------------------------------------------

		file_name_without_suffix = file_name[:file_name.rfind('.')]
		file_html_link = f"[{file_name_without_suffix}]({file_name_without_suffix + '.html'})"
		current_file_mtime = datetime.datetime.fromtimestamp(item[1])

		if time_for_compare > current_file_mtime:
			if time_for_compare.replace(month=1) > current_file_mtime:
				print('', file=output_file)
				print(prefix_year + current_file_mtime.strftime('%Y') + '年', file=output_file)

			print('', file=output_file)
			print(prefix_month + current_file_mtime.strftime('%m') + '月', file=output_file)
			# print("|最后修改时间|链接|", file=output_file)
			# print("|--|--|", file=output_file)
			time_for_compare = current_file_mtime.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

		print("- " + datetime.datetime.fromtimestamp(item[1]).strftime('%Y.%m.%d') + 
			"："  + file_html_link, 
			file=output_file)


if __name__ == "__main__":

# ---- 命令行参数处理 --------------------------------------------------------------------

	folder_path = sys.argv[1] if len(sys.argv) > 1 else "./md"


# ---- 错误处理 -------------------------------------------------------------------------

	if not os.path.exists(folder_path):
		print(f"{sys.argv[0]}: \033[31m[Error]\033[0m \
			path \"{folder_path}\" does not exists", file=sys.stderr)
		exit(1)


# ---- 分类目录 --------------------------------------------------------------------------

	with open("./md/分类.md", 'w') as f:
		file_prifex = \
"""\
# 分类
> 技术相关的：
> - 笔记：适合查阅，不适合阅读  
> - 博客：相对比较适合阅读  
"""
		print(file_prifex, file=f)
		make_toc_by_category(folder_path, output_file=f)


# ---- 时间目录 --------------------------------------------------------------------------
	with open("./md/时间轴.md", 'w') as f:
		file_prifex = \
"""\
# 时间轴
> 本来应该搞个以创建时间排序的时间轴，但是Linux似乎不会记录文件最初的创建时间，所以只能以最后修改时间来排序了。
所以有些文件可能很早就创建了，只是后来做了一些小修改，因而排到了前面

> 不知道为什么，所有的markdown文件的修改时间突然都被更新了一遍，导致现在的时间轴里的文章几乎都在同一天了……好烦。
"""
		print(file_prifex, file=f)
		make_toc_by_mtime(folder_path, output_file=f)
