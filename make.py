# -*- coding: utf-8 -*-

import os
import subprocess

def get_md_and_html_targets(md_dir, html_dir):
    mapping_table_list = []
    file_pattern = '.md'

    for dirpath, _, file_list in os.walk(md_dir):
        for file in file_list:
            if file.endswith(file_pattern):
                filename_without_suffix = file[:file.rfind('.')]

                html_file = os.path.join(html_dir, filename_without_suffix + '.html')
                md_file = os.path.join(dirpath, file)

                if (not os.path.exists(html_file)) or ( os.path.getmtime(md_file) > os.path.getmtime(html_file)):
                    mapping_table_list.append( (md_file, html_file) )

                # 是目录就直接构建了吧
                if file.startswith('分类') or file.startswith('时间轴'):
                    mapping_table_list.append( (md_file, html_file) )

    return mapping_table_list


# Example usage:
if __name__ == "__main__":

# ---- 初始工作 --------------------------

    template_renderer = './tr'
    template_html = './web_skeleton/skeleton.html'

    md_dir = './md'
    html_dir = './html'
    css_dir = './css'
    js_dir = './js'
    img_dir = './media/image'

    mapping_table_list = get_md_and_html_targets(md_dir, html_dir)  # map md to html

# ---- index ---------------------------------
    
    # 主页还是单独处理吧
    index_md = "index.md"
    index_html = "index.html"
    index_template = './web_skeleton/index.html'    

    if not os.path.exists(index_html) or os.path.getmtime(index_md) > os.path.getmtime(index_html):
        print(f"\033[0;33m[....] Building index\033[0m")
        os.system( f"{template_renderer} {index_template} -o {index_html} -p markdown_file.md={index_md}")

# ---- 更新目录md文件 -------------------------

    print(f"\033[0;33m[....] Building markdown of toc\033[0m")
    os.system("python3 make_toc.py")

# ---- 构建html -------------------------

    for md_file, html_file in mapping_table_list:
        md_file_basename_without_suffix = os.path.basename(md_file)[:os.path.basename(md_file).rfind('.')]
        print(f"\033[0;33m[....] Building '{html_file}'\033[0m")
        build_command = template_renderer + ' ' + template_html +\
            " -o " +  html_file + \
            " -p title=" + md_file_basename_without_suffix + \
            " -p markdown_file.md=" + md_file
        print(build_command)
        os.system(build_command)
