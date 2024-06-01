#!/usr/bin/python3

from pathlib import Path
import sys

if len(sys.argv) != 2:
	print("Usage: python3 make_toc.py path_name", file=sys.stderr)
	exit(-1)
directory = sys.argv[1]
path = Path(directory)

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


ls(path, 2)