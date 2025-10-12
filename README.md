

## 提示词
### 依赖检查模块：

模块有四个输入，第一个输入是一个全局配置config.yaml，第二个输入是一个文件夹路径，该路径中存放着多个markdown文件（文件夹中可能有嵌套的子文件夹中也有markdown文件），第三个输入是一个文件夹路径，该路径中存放着多个html文件（文件夹中不存在文件夹了），第四个输入是一个json格式的cache文件（此文件可能不存在，若不存在，则需要创建一个），里面存放着markdown文件的一些信息（如果没有这个文件，那么会在后面的流程中创建这个文件）。

全局配置config.yaml的格式如下：
```yaml
md_dir: md
html_dir: html
partials_dir: partials
template_dir: template
template: template.mustache
auto_h1: true           # 自动生成标题h1标签
has_comment: true       # 评论
has_toc: true           # 目录
add_to_category: true   # 添加至“分类”页面？
add_to_timeline: true   # 添加至“时间轴”页面？

# markdown解析扩展
md_parser_extension: ['fenced_code', 'tables', 'footnotes', 'nl2br']

site: "https://code-pigeon.github.io/blog/"
```
用python的yaml库读入到一个变量里就行了。

接着需要建立一个json文件格式的cache文件，这个文件中存储着很多键值对，键是markdown文件的绝对路径，值是更多的键值对，如下所示：
```json
{
  "D:/DataDisk/workspace/blog/md/index.md": {
    "file_updated": 1745767345.34321,
    "should_build": false,
    "title": "我的第一篇博客",
    "category": [],
    "date": "25/04/25/21:34",
    "updated": null,
    "link": "https://code-pigeon.github.io/blog/index.html",
    "quote_link": "https://code-pigeon.github.io/blog/index.html",
    "description": "<p>我的第一篇博客，测试；2025-05-03 16:06:40；html/</p>\n"
  },
  "D:/DataDisk/workspace/blog/md/test/test - 副本.md": {
  	"file_updated": 1745592852.878918,
    "should_build": true,
    "title": "莫蓝特受伤了",
    "category": [
      "test", "篮球"
    ],
    "date": "25/04/25/11:40",
    "updated": null,
    "link": "https://code-pigeon.github.io/blog/test - 副本.html",
    "quote_link": "https://code-pigeon.github.io/blog/test%20-%20%E5%89%AF%E6%9C%AC.html",
    "description": "<h2 id=\"_1\">莫兰特又受伤了</h2>\n"
  }
}
```
所以接下来的任务就是要把这么一个映射给做出来。

从全局配置的`md_dir`获取markdown文件所在的文件夹，然后遍历获取该文件夹中所有markdown文件的绝对路径，这个就是cache中的键，接下来要读取markdown文件的修改日期，也就是`file_updated`字段。
然后是决定`should_build`的值，这里的`should_build`表示这个markdown文件是否需要被构建（如果已经存在对应的html的话就不需要构建），规则如下：
1. 如果cache中找不到对应的markdown文件，则新增记录到cache中，should_build为true
2. 如果cache中找到对应的markdown文件，但无对应html，should_build为true
3. 如果cache中找到对应的markdown文件，且markdown的文件修改时间`file_updated`大于cache中记录的`file_updated`，should_build为true
4. 如果cache中找到对应的markdown文件，且markdown的文件修改时间`file_updated`小于cache中记录的`file_updated`，should_build为false

这个过程中涉及到一个问题，就是要找到markdown对应的html，规则是这样的，
在config.yaml中有一个字段是`html_dir`里面存放着markdown渲染为html之后存放的位置，所以存在md_dir和html_dir两个文件夹，里面分别放着markdown源文件和html文件，那么有可能出现以下情况：
1. 有md，无对应html，这种情况前文已经叙述过了，新增cache记录，should_build为true
2. 有md，有对应html，这种情况不处理
3. 有html，但没有对应的md，这种情况需要把该html清理掉

但是这里的md_dir是存在子文件夹的，子文件夹的实际作用是起到分类的作用，假如md文件夹的内容如下：
```
md
├── index.md
├── 瞎聊
│   ├── test.md
│   └── 二级分类
│       └── 今天是个好日子.md
└── 文章
    └── 《论至九站》.md

```
那么index.md就是无分类的，test.md的分类为`["瞎聊"]`，而今天是个好日子.md的分类则为`["瞎聊", "二级分类"]`，也就是说，`category`这个字段中，第一个值为1级分类，第二个值为2级分类，以此类推。

然后这些md文件渲染为html文件之后，会全部放置在html_dir的根目录下，html_dir中并不会有子文件夹。所以在寻找md文件和对应的html时，还需要注意这点细节。

然后对于所有should_build为true的markdown文件，需要真正的去打开markdown文件，读取信息了。
markdown文件的内容分为两个部分，一个是头部的信息，另一部分是正文：
```markdown
---
title: 我的第一篇博客
date: 25/04/25/21:34
updated: 25/10/11/15:38
---	
{{title}}，测试；{{html_dir}}

{{> fancy_banner }}

# 鸽子窝
> 欢迎来到鸽子窝
<!-- > 喜欢回忆过去，喜欢幻想将来，唯独不喜欢珍惜现在。 -->

## 关于我
### 爱好
```
如你所见，这里的头部信息存放了一些需要放入cache记录中的字段。此时只需要读取头部的信息就行了，正文暂且不管。

可以看到，头部信息中并没有分类字段`category`的数据，因为分类是通过md_dir指示的文件夹中的子文件夹来实现分类的，记得吗。

还有link和quote_link的话，是通过config中的site字段和markdown文件的生成的对应html文件的文件名拼合而成的。

比如markdown文件的路径如果是`D:/DataDisk/workspace/blog/md/瞎聊/二级分类/test.md`（md这个路径由config中的md_dir字段指示），那么它对应的html的路径应该是`D:/DataDisk/workspace/blog/html/test.md`（html这个路径由config中的html_dir字段指示），所以其实博客的根目录就是`D:/DataDisk/workspace/blog/`，所以需要从此处截断，提取`html/test.md`和site字段的`https://code-pigeon.github.io/blog/`组合到一起，所以link就是`https://code-pigeon.github.io/blog/html/test.md`，此时link里没有出现unicode编码，所以quote_link和link相同。如果link中出现了unicode，那么quote_link就需要将其中的Unicode进行转义处理。

最后`description`此字段暂不处理。

到此为止，cache文件的构建也就已经完成了。

最后说明，此模块所用依赖为：
- python-frontmatter
- PyYAML

注意：
- 模块中所有的路径都要使用linux风格的路径
- 文件的修改时间直接用时间戳来存储
- 如果cache文件的修改日期比config的修改日期要小，那么所有md的should_build都为true

现在对于这个模块我有一个新的需求，那就是md文件和html文件的文件名，如果有以前缀"NOCHECK_“开头的，那么它们将不参与这个依赖检查。你能帮我添加这个功能吗？只需要写出需要修改的部分就可以了

我需要添加一个需求，如果在缓存中的md文件路径，实际上找不到这个路径对应的文件，那么应该把这条记录删除。你可以帮我添加一下吗？只需要写出需要修改的部分就行了


测试：
- 放些没有对应的html的md文件，看看是否标注should_build为true
- 放些有对应html的md文件，先构建一遍cache（cache记录文件的修改日期），再构建第二遍，看看这些md文件是否标注should_build为false
- 放一些不存在对应md文件的html文件在html_dir中，看看是否能够正确清理
- 构建cache文件一次之后，修改config文件，看看should_build是否全部标记为true


### 解析渲染模块
模块有2个输入，1个输出。
输入1是一个全局配置文件config.yaml，输入2是一个cache.json文件。

config.yaml的内容大概如下：
```yaml
md_dir: md
html_dir: html
partials_dir: partials
template_dir: template
template: template.mustache
auto_h1: true           # 自动生成标题h1标签
has_comment: true       # 评论
has_toc: true           # 目录
add_to_category: true   # 添加至“分类”页面？
add_to_timeline: true   # 添加至“时间轴”页面？

# markdown解析扩展
md_parser_extension: ['fenced_code', 'tables', 'footnotes', 'nl2br']

site: "https://code-pigeon.github.io/blog/"

template: 'post.mustache'
```

大概就是一些控制markdown格式的信息。

直接用python的yaml读取到一个变量即可。

接下来需要从config.yaml读取的`partials_dir`字段去读取文件夹下的所有`.mustache`文件，并存储在一个变量中。

然后是需要打开cache.json文件，这个文件中存储着很多键值对，键是markdown文件的绝对路径，值是更多的键值对，其内容如下：
```json
{
  "D:/DataDisk/workspace/blog/md/index.md": {
    "file_updated": 1745767345.34321,
    "should_build": false,
    "title": "我的第一篇博客",
    "category": [],
    "date": "25/04/25/21:34",
    "updated": null,
    "link": "https://code-pigeon.github.io/blog/index.html",
    "quote_link": "https://code-pigeon.github.io/blog/index.html",
    "description": "<p>我的第一篇博客，测试；2025-05-03 16:06:40；html/</p>\n"
  },
  "D:/DataDisk/workspace/blog/md/test/test - 副本.md": {
  	"file_updated": 1745592852.878918,
    "should_build": true,
    "title": "莫蓝特受伤了",
    "category": [
      "test", "篮球"
    ],
    "date": "25/04/25/11:40",
    "updated": null,
    "link": "https://code-pigeon.github.io/blog/test - 副本.html",
    "quote_link": "https://code-pigeon.github.io/blog/test%20-%20%E5%89%AF%E6%9C%AC.html",
    "description": "<h2 id=\"_1\">莫兰特又受伤了</h2>\n"
  }
}
```
获取json文件中所有的键（即所有markdown文件的绝对路径），然后对于**所有**字段`should_build`为true的markdown文件，需要执行下一个解析构建流程。

构建流程首先是要打开markdown文件，markdown文件内容分为两部分，markdown的头部控制信息和正文，如下所示：
```markdown
---
title: 我的第一篇博客
date: 25/04/25/21:34
updated: 25/10/11/15:38
has_toc: false
---	
{{title}}，测试；{{html_dir}}

{{> fancy_banner }}

# 鸽子窝
> 欢迎来到鸽子窝
<!-- > 喜欢回忆过去，喜欢幻想将来，唯独不喜欢珍惜现在。 -->

## 关于我
### 爱好
```
读取markdown的头部信息之后，需要做一件重要的事情，那就是需要用头部信息去更新全局配置的，比如说头部信息里的`has_toc`字段为true，但是markdown中也可能出现`has_toc`字段为false，此时需要用markdown头部的false去覆盖全部配置的true。另外，markdown头部中也可能出现全局配置没有的字段，比如`title`，此时需要新增这个字段。后文将称这个更新后的配置为局部配置

（值得注意的是，此阶段需要遍历构建非常多的markdown文件，但是每次合并markdown头部和全局配置时，都得用config.yaml里的内容和当前的markdown头部进行合并，两次相邻的markdown处理流程之间不能相互影响。）

然后是markdown的正文部分，我们需要把markdown正文部分渲染为html（就用python的markdown库即可），此时有一个重要的步骤要插入执行，那就是把cache.json中的`description`字段填充为渲染好的html（这里需要注意，如果html大于300字符，那么只提取前300字符的内容，但是如果第300个字符还在某个html标签中，那么必须继续一直提取到html标签结束才能够停止），我想把渲染为html的markdown正文本身作为一个部分模板，因为markdown正文中可能也会出现一个模板变量需要被替换掉，所以需要把解析后的内容也存为一个部分模板。

接着是进行模板替换操作，局部配置中（指的是全局配置和markdown头部融合之后的局部配置）有一个字段是`template_dir`和另一个字段`template`，这两个字段组合起来就是模板文件的路径，比如`template_dir`是template，`template`是post.mustache，那么组合起来模板文件的路径就是`template/post.mustache`，此时就以这个文件为模板，然后以局部配置为上下文，以部分模板变量为部分模板，用`chevron.render`进行模板替换。生成的html文件保存在局部配置中html_dir所指示的路径中，文件名和markdown的文件名相同（当然后缀名要改为html）。

最后注意：
- markdown渲染html使用python的Markdown库
- 模板引擎使用chevron
- 提取markdown头部信息使用python-frontmatter库

### 扩展模块rss
模块有2个输入，一个输出。

输入1为一个config.yaml文件，其内容如下：
```yaml
# --- 博客信息 --------------------------------------------------------
blog_name: 乌鸦之家
blog_signature: '岁岁年年，碎碎念念'
author: "乌鸦"
footer_note: © 2025 乌鸦之家

site: "https://code-pigeon.github.io/blog/"     # 博客基址
```

输入2为一个cache.json文件，其内容如下：
```json
{
  "D:/DataDisk/workspace/blog/md/index.md": {
    "file_updated": 1760234911.6160536,
    "should_build": false,
    "title": "我的第一篇博客",
    "category": [],
    "date": "25/04/25/21:34",
    "updated": null,
    "link": "https://code-pigeon.github.io/blog/html/index.html",
    "quote_link": "https://code-pigeon.github.io/blog/html/index.html",
    "description": "{{title}}，测试；{{build_time}}；{{html_dir}}\n这里应该是fancy_banner所在的位置{{&gt; fancy_banner }}。。。。。。。。。。。。。。。。。。\n所以说其实部分模板中不能嵌套部分模板？\n{{&gt; test }}\n@####################################\n鸽子窝\n\n欢迎来到鸽子窝\n\n 喜欢回忆过去，喜欢幻想将来，唯独不喜欢珍惜现在。"
  },
  "D:/DataDisk/workspace/blog/md/test/test - 副本.md": {
    "file_updated": 1745588576.3264618,
    "should_build": false,
    "title": "莫蓝特受伤了",
    "category": [
      "test"
    ],
    "date": "25/04/25/11:40",
    "updated": null,
    "link": "https://code-pigeon.github.io/blog/html/test - 副本.html",
    "quote_link": "https://code-pigeon.github.io/blog/html/test%20-%20%E5%89%AF%E6%9C%AC.html",
    "description": "莫兰特又受伤了\n伺机待发接送地方军哦i\na mama:\n这公司开始严抓考勤了\na mama:\n一个Q迟到4次都要被说\na mama:\n[动画表情]\na最好看的姐姐:\n倒闭前兆\na最好看的姐姐:\n[动画表情]\na mama:\n以前每年还有工资普调，38,618，双11还发奖金\na mama:\n去年双11开始不发奖金了\na mama:\n今年普调也没有\na mama:\n然后今天hr还找我们领导投诉考勤问题了\na mama:\n这么计较上班时间，那下班晚了怎么不补钱给我\na道:\n奴伙，刀郎去年最红的歌叫什么？\n🐦:\n罗刹海市"
  }
}
```
现在我需要根据这个cache.json中的记录，输入一个feed.xml文件，就是rss2.0。它的大概内容你可以参考：
```xml
<rss version="2.0">
<channel>
<title>码鸽</title>
<link>https://code-pigeon.github.io/blog/</link>
<description>咕~码鸽的咕言咕语</description>
<item>
<title>我也用cloudflare R2来做图床了</title>
<link>https://code-pigeon.github.io/blog/web/html/20250421cloudflare-as-image-host.html</link>
<pubDate>Mon, 21 Apr 2025 19:16:00 +0800</pubDate>
<guid isPermaLink="true">https://code-pigeon.github.io/blog/web/html/20250421cloudflare-as-image-host.html</guid>
<description><![CDATA[在，我提到了我对图床的要求。找了不少免费图床，最后只有一家图床满足我的要求。复述一下我对图床的要求：我希望图床能够保留文件的文件名，而不是随机给我另外生成一个。（这样能够方便我实现备用图床的机制，详见我之前的博客图床的选择今天逛博客的时候又看到了别人用大名鼎鼎的cloudflare R2来做图床的，不知道为什么记忆错乱，老是以为自己试过这个cloudflare了，其实并没有，于是今天尝试了一下，没想到这么简单，而且它也满足我对图床的要求（就是图片的链接有点丑）。...... <a href='https://code-pigeon.github.io/blog/web/html/20250421cloudflare-as-image-host.html'>Read more</a>]]></description>
</item>
</channel>
</rss>
```
我说明一下，这个`<title>码鸽</title>`字段来自于config.yaml中的blog_name字段，`<link>https://code-pigeon.github.io/blog/</link>`来自于config.yaml中的site字段，`<description>咕~码鸽的咕言咕语</description>`来自于config.yaml中的blog_signature字段。然后item下面的字段的话，你应该看得明白，`<title>我也用cloudflare R2来做图床了</title>`对应cache.json中的title，`<link>https://code-pigeon.github.io/blog/web/html/20250421cloudflare-as-image-host.html</link>`对应cache.json中的quote_link，pubDate对应date，其它的我就不赘叙了。

然后有一个特别重要的要求，就是这些feed的item要按照cache.json中所记录的date字段进行排序。如果date字段为空，那么这个记录就不加入feed中。

然后最多只能有10个feed 的item。

另外，这个`<pubDate>`要特别注意格式，好像是有个规范叫rfc822是吧，反正你要处理到它符合rss2.0的规范。

注意：
构建feed.xml使用python自带的xml库，这样才能使代码简单一点

差点忘了，时间要能够支持以下格式：
"%y/%m/%d/%H:%M",  # 24/9/24/19:05
        "%Y/%m/%d/%H:%M",  # 2024/9/24/19:05
        "%Y/%m/%d",         # 2024/9/24
        "%y/%m/%d",         # 24/9/24
        "%Y-%m-%d",         # 2024-9-24

用python帮我实现一下这个模块