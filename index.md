# 鸽子窝
> 欢迎来到鸽子窝
<!-- > 喜欢回忆过去，喜欢幻想将来，唯独不喜欢珍惜现在。 -->

## 关于我
暂时保密

## 技术相关
### 建站环境和工具
- 环境
	- Ubuntu20.04 x86-64
- 工具
	- markdown解析和模板引擎：在开源的markdown解析器[cmark-gfm](https://github.com/github/cmark-gfm)（cmark的分支）之上做了一些小修改，并且融合了自己写的简易模板引擎，做成了一个将模板引擎和markdown解析渲染功能合并起来的小工具。
	- 代码高亮：[highlight.js](https://highlightjs.org/)
	- html目录：[tocbot.js](http://tscanlin.github.io/tocbot/)
	<!-- - 模板引擎：template_renderer（自己写的微型模板引擎） -->
- 其它
	- css样式参考：[retro](https://github.com/markdowncss/retro)
	- 侧边栏参考：[simple-sidebar](https://startbootstrap.com/template/simple-sidebar)
	- 代码块的css样式参考：[panda-syntax-dark](https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/panda-syntax-dark.min.css)

### 存在的问题
暂未发现。

### 版本日志（开发视角）
- 1.0.2
	- 将markdown解析器和模板引擎融合成一个单独的应用；
	- html的`id`属性的生成从前端js代码转移至后端——在cmark-gfm上进行细微修改，渲染为html时会自动增加`id`属性；
	- 抛弃了`html`文件夹下放置子文件夹的思路，现在的`.html`文件全部直接放置于`html`文件夹下（除了`index.html`）；
	- 渲染html页面时不再使用在构建脚本中计算相对路径的方式对静态资源文件进行定位，改为手动编写；
	- `index.html`和其它`.html`的模板分离，构建也分开处理；
	- 不再使用make作为构建脚本，转为python；
	- 新增“时间轴”目录，原来的目录取名为“分类”；
	- 开启了脚注功能，细微修改了脚注样式；
- 1.0.1
	- markdown解析器更改为cmark-gfm；

