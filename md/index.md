---
title: 其实这是首页
auto_h1: false
---	
# 乌鸦之家
> 感谢光临

## 关于我
### 爱好
- 🏀：篮球
- 🎤：唱歌
- 🎱：桌球
- 🏊︎：游泳
- 🖊︎：记录
- 📔：看小说
- 🏓：乒乓球
- 🐘：中国象棋（曾经的爱好）
- 🖌：画画（曾经的爱好）

### 我的其它社媒账号
- 抖音：[乌鸦有想法](https://www.douyin.com/user/MS4wLjABAAAABuryJcmnmTlY6lTkKhc-YDd3AH6_KzwiRnM-WaCizKk)
- B站：[乌鸦有想法](https://space.bilibili.com/516728425)
- 公众号：乌鸦碎碎念

## 联系我
- 邮箱：`code_pigeon@163.com`

## 建站相关
### 建站环境和工具
- 环境
	- 代码编辑器：[sublime text](https://www.sublimetext.com/)
	- 操作系统、处理器架构：Windows11 x86-64
- 工具
	- 博客构建器：gezi（自己写的，感觉不太好用，目前不考虑开源）
		- 模板引擎：[chevron](https://github.com/noahmorrison/chevron)
		- markdown解析：[python-markdown](https://github.com/Python-Markdown/markdown)
	- 代码高亮：[highlight.js](https://highlightjs.org/)
	- html目录：[tocbot.js](http://tscanlin.github.io/tocbot/)
	- 版本控制：[git](https://git-scm.com/)
	- 评论系统：[Valine](https://valine.js.org/)
- 涉及的编程语言
	- 前端三剑客（html、css、javascript）
	- python
- 其它
	- css样式参考：[retro](https://github.com/markdowncss/retro)
	- 侧边栏参考：[simple-sidebar](https://startbootstrap.com/template/simple-sidebar)
	- 代码块的css样式参考：[panda-syntax-dark](https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/panda-syntax-dark.min.css)
	- 编程助手：[深度求索（deepseek）](https://www.deepseek.com/)

### 下一步目标
- 可能要考虑放弃Valine评论系统了，阅读量都很少，别说评论了。
- 添加扩展的依赖检查功能
- 添加对模板文件、部分模板文件的依赖检查

### 博客构建器版本日志
1.1.3

- 全新的架构
- 添加缓存设计
- rss订阅

1.1.1

- 将工作环境迁移至Windows；
- 放弃C语言开发，全面倒向python；
	- 模板引擎：[chevron](https://github.com/noahmorrison/chevron)
	- markdown解析：[python-markdown](https://github.com/Python-Markdown/markdown)
- 添加配置系统；
- 添加对markdown元数据（front matter）的支持；
- CSS：创建、更新时间标签；

1.0.6

- 修改评论区头像cdn：Gravatar ==> cravatar

1.0.5

- 修复bug：首页无法统计阅读量

1.0.4

- 修复bug：不在正文中的行内代码块的背景色无法显示；
- 添加文末的创作共用许可证声明；
- 添加功能：阅读量统计；

1.0.3

- 新增评论系统Valine；

1.0.2

- 将markdown解析器和模板引擎融合成一个单独的应用；
- html的`id`属性的生成从前端js代码转移至后端——在cmark-gfm上进行细微修改，渲染为html时会自动增加`id`属性；
- 抛弃了`html`文件夹下放置子文件夹的思路，现在的`.html`文件全部直接放置于`html`文件夹下（除了`index.html`）；
- 渲染html页面时不再使用在构建脚本中计算相对路径的方式对静态资源文件进行定位，改为手动编写；
- `index.html`和其它`.html`的模板分离，构建也分开处理；
- 不再使用make作为构建脚本，转为python；
- 新增“时间轴”目录，原来的目录取名为“分类”；
- 开启了脚注功能，细微修改了脚注样式；

1.0.1

- markdown解析器更改为cmark-gfm；

### 为什么搭博客？（都是废话）
我原本很不喜欢做笔记。后来发现很多时候学过的某个知识总会在未来的某些时候用到，如果不做笔记，用到这些知识时就会以为自己没学过，然后上网搜索资料，越搜越觉得熟悉，然后恍然大悟自己学过，但是其实又忘得差不多了，还是得浪费时间重新学习一遍。所以后来开始做笔记。

但是一开始是纸质的笔记，做起来效率非常低，而且查阅不便，复制粘贴更是想都别想。所以又开始使用电子笔记。

一开始做电子笔记试过

1. word（软件太笨重，遂放弃）
2. latex（软件同样很笨重，而且写起来效率巨低，有种在写代码而不是笔记的错觉）
3. 电子手账（好用的软件不多，而且好像很多手账软件都有自己的文件格式，不喜欢；手写的内容查阅起来也是非常不方便）

最后发现了[markdown](https://markdown.com.cn/)这种轻量级的标记语言，文件格式只是简单的文本格式，只需要一个文本编辑器就可以记录，非常满足我的喜好。所以又开始将markdown作为做笔记的主要方式。

后来虽然写笔记爽了，但笔记越写越多，查阅越来越困难，而且文件都是本地的，有时不在自己的设备上工作，笔记也全没法看了。

但好像很多markdown笔记软件都可以解决这些问题，我为啥不用呢？

我很不喜欢受制于别人写的软件的限制，例如它们的外观让我不满意，但我却不能随心所欲地修改；又或者是这些软件哪天突然宣布收费，这时候我还需要对于这种变故作出自己的选择……

如果我没有计算机知识，那么我大概也会选择使用专业人员开发的软件。但我确实有，所以为什么不自己写一个完全让自己称心如意的工具呢？

所以我选择了搭建博客，博客页面的功能、外观全部可以由自己决定。

因为博客毕竟还是面向网络的，我无法假定这个博客永远没有访客，这也许可以督促我把博文写得更细致一些吧（有些文字是真的写完回头再看自己也看不懂）。所以现在的博客也好像不仅仅是记笔记而已了，出现了很多分享性的博文。

