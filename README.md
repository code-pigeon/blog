

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


### 扩展模块时间轴
模块有3个输入，1个输出
输入1为一个config.yaml文件，其内容大概如下：
```yaml
md_dir: "md/"
html_dir: "html/"
template_dir: "template/" # 模板的路径
partials_dir: partials  # 部分模板的路径
```
用python的yaml库读取到一个变量中即可。


输入2为一个.mustache模板文件，这个文件存在config.yaml中template_dir指示的路径下，其内容大概如下：
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{{title}}}</title>
  <link href="{{css_url}}index.css" rel="stylesheet">
  <!-- syntax highlighting -->
  <link rel="stylesheet" type="text/css" href="{{css_url}}code_highlight.css">
  <link rel="stylesheet" type="text/css" href="{{css_url}}date_and_updated.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <!-- table of content -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/tocbot/4.27.4/tocbot.min.js"></script>
</head>
<body>
  <header>
    <!-- 左侧个人形象部分 -->
      <div class="profile">
          <img src="{{{img_url}}}pigeon2.png" alt="个人头像" class="avatar">
          <span class="nickname">{{{author}}}</span>
      </div>
      
      <!-- 右侧导航菜单（保持原有结构） -->
    <nav>
        <ul>
          {{#nav}}
            <li><a href="{{url}}">{{label}}</a></li>
          {{/nav}}
        </ul>
    </nav>
  </header>
  <div class=fluid> 
    <h1 id="时光轴">时光轴</h1>
    {{> content }}

    <br />
    <hr />

    <!-- visitor -->
    <!-- id 将作为查询条件 -->
    <span id="/blog/{{html_dir}}{{{ stem }}}.html" class="leancloud_visitors" data-flag-title="{{{page_title}}}">
        <em class="post-meta-item-text">阅读量 </em>
        <i class="leancloud-visitors-count">0</i>
    </span>
    <!-- \visitor -->

    <br />

  </div>

  {{#has_toc}}
  <div class="left-sidebar">
    <div class="toc"></div>
    <div class="toc-toggle"></div>
  </div>
  {{/has_toc}}

  <!-- /////////////////////////////////////////////////////////////////////////////////////////////////////////// -->

  <!-- /////////////// script region //////////////// -->

  <script src="../js/code_highlight.js" type="text/javascript"></script>
    
  <!-- table of cotent -->
  {{#has_toc}}
  <script src="../js/toc.js" type="text/javascript" ></script>
  {{/has_toc}}

  <script type="text/javascript">
    // 定义备用路径
    const fallbackBaseUrl = "{{{img_url2}}}"; // 备用路径

    // 监听所有 .fluid 下的 img 标签
    document.addEventListener('DOMContentLoaded', function() {
      const images = document.querySelectorAll('div.fluid img, div.profile img');
      images.forEach(function(img) {
        img.addEventListener('error', function() {
          const currentSrc = img.src;

          // 如果当前已经是备用路径，则移除 src（避免无限循环）
          if (currentSrc.includes(fallbackBaseUrl)) {
            img.removeAttribute('src'); // 仅显示 alt
            return;
          }

          // 替换主路径为备用路径（保留文件名）
          const fileName = currentSrc.split('/').pop(); // 提取文件名（如 "test.png"）
          const newSrc = fallbackBaseUrl + fileName;    // 拼接备用路径
          img.src = newSrc; // 尝试加载备用图
        });
      });
    });
  </script>

</body>
</html>
```
看到其中的`{{> content }}`了吗，这个部分模板是接下来需要经过处理之后才能获得的。

输入3为一个cache.json文件，其内容如下：
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

需要对这些记录进行排序之后，生成时光轴页面的主要内容（即博文链接根据时间进行排序）（注意，这里的链接使用相对路径，即`https://code-pigeon.github.io/blog/html/index.html`的链接只要为`index.html`即可），生成的页面内容将作为一个部分模板content，最后插入到.mustache的`{{> content }}`处，页面内容的排版和视觉风格由你来定，当然，其.mustache模板文件的风格我已经写好了，你可以写个风格搭一点的排版和css。
```css
/*//////////////////////////////////////////////////////////////////////////////////////*/

/* begin retro (https://github.com/markdowncss/retro) */

code {
  /* 行内代码 */
  margin: 0 0.2rem;
  padding: 0 0.3rem;
  background-color: #303841;
  border-radius: 0.25rem;
/*  border: 1px solid #505050;*/
}

pre,
pre code {
  font-family: Source Code Pro,DejaVu Sans Mono,Ubuntu Mono,Anonymous Pro,Droid Sans Mono,Menlo,Monaco,Consolas,Inconsolata,Courier,monospace,PingFang SC,Microsoft YaHei,sans-serif;

/* ---- print ---------------------------------------------------------------------------------------------*/

@media print {
  *,
  *:before,
  *:after {
    background: transparent !important;
    color: #000 !important;
    box-shadow: none !important;
    text-shadow: none !important;
  }

  a[href]:after {
    content: " (" attr(href) ")";
  }

  abbr[title]:after {
    content: " (" attr(title) ")";
  }

  a[href^="#"]:after,
  a[href^="javascript:"]:after {
    content: "";
  }

  pre,
  blockquote {
    border: 1px solid #999;
    page-break-inside: avoid;
  }

  thead {
    display: table-header-group;
  }

  tr,
  img {
    page-break-inside: avoid;
  }

  img {
    max-width: 100% !important;
  }

  p,
  h2,
  h3 {
    orphans: 3;
    widows: 3;
  }

  h2,
  h3 {
    page-break-after: avoid;
  }
}
/* ---- end print ---------------------------------------------------------------------------------------------*/

a {
/*  color: #01ff70;*/
  text-decoration: none;
  color: #45a9f9;
/*  font-family: "宋体", "SimSun", cursive;*/
  font-family: "宋体", "SimSun";
}

a:hover,
a:focus,
a:active {
/*  color: #2ecc40;*/
  color: #62bfff;
}


.retro-no-decoration {
  text-decoration: none;
}

html {
  font-size: 12px;
  transition: all 0.35s ease 0.1s;
}

@media screen and (min-width: 32rem) and (max-width: 48rem) {
  html {
    font-size: 14px;
  }
}

@media screen and (min-width: 48rem) {
  html {
    font-size: 16px;
  }
}

p,
.retro-p {
  font-size: 1rem;
  letter-spacing: 0.1rem; 
/*  margin-bottom: 1.3rem;*/
}

h1,
.retro-h1,
h2,
.retro-h2,
h3,
.retro-h3,
h4,
.retro-h4 {
  margin: 1.414rem 0 .5rem;
  font-weight: inherit;
  line-height: 1.42;
  font-family: "宋体", "SimSun", sans-serif;
  color: #fff;
}

h1,
.retro-h1 {
  margin-top: 0;
  margin-bottom: 0;
/*  margin-bottom: 4rem;*/
  font-size: 3.88rem;
}

h2,
.retro-h2 {
  font-size: 2.78rem;
}

h3,
.retro-h3 {
  font-size: 1.9rem;
}

h4,
.retro-h4 {
  font-size: 1.414rem;
}

h5,
.retro-h5 {
  font-size: 1.121rem;
}

h6,
.retro-h6 {
  font-size: .88rem;
}

small,
.retro-small {
  font-size: .707em;
}

/* https://github.com/mrmrs/fluidity */

img,
canvas,
iframe,
video,
svg,
select,
textarea {
  max-width: 100%;
}

html,
body {
/*  background-color: #222;*/
  background-color: #22262a;
  min-height: 100%;
}

body {
  color: #bbb;
  font-family: Helvetica Neue, NotoSansHans-Regular,AvenirNext-Regular,arial,Hiragino Sans GB,Microsoft Yahei,WenQuanYi Micro Hei,serif;
/*  font-family: system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;*/
  line-height: 1.45;
}

pre {
/*  background-color: #333;*/
/*  background-color: #393f46;*/
}

blockquote {
/*  border-left: 3px solid #01ff70;*/
  border-left: 3px solid #45a9f9;
  background-color: #66666619;
  padding: 0.1rem 1rem;
/*  font-size: smaller;*/
/*  font-family: "楷体", "KaiTi", cursive;*/
/*  font-style: italic;*/
}

/* end retro */


/*///////////////////////////////////////////////////////////////////////////////////////////*/

/* begin left-sidebar */

.left-sidebar{
  position: fixed;
  top: 50%; /* Adjust as per your layout */
  left: 0%; /* This will position the div on the left side */
  transform: translate(0, -50%); /* Center vertically based on its own height */

  display: flex;

}

.toc-toggle{
  width: 20px;
  height: 3.2rem;
  background-color: #45a9f977;
  border-radius: 0 5px 5px 0;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
/*  margin-top: 0.4rem;*/
  cursor: pointer;
}

.toc-toggle:hover{
  background-color: #45a9f9aa;
}

.toc-hidden{
  margin-left: -17.5rem;  /*  此值等于.toc.width + .toc.padding-right */
}

/* end left-sidebar */


/* begin tocbot */

.toc {
  background-color: #313438;
  padding: 1rem 0;
  padding-right: 0.5rem;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
  overflow-y: auto;
  border-radius: 0 0.1rem 0.5rem 0;
  max-height: calc(100vh - 40px); 
  width: 17rem;
  transition: all 0.45s ease;
}

.toc a{
  color: white;
}

.toc-list{
  padding-left: 1.9rem;
}

/* Style for the main list items */
.toc-list-item {
  list-style: none;
/*  margin-bottom: 8px;*/
}

/* Style for the links */
.toc-link {
  text-decoration: none;
  color: #333;
  display: block;
  padding: 5px 5px 5px 10px;
  margin-right: 10px;
  border-radius: 3px;
  transition: background-color 0.3s ease;
}

/* Hover effect for the links */
.toc-link:hover {
  background-color: #e0e0e02e;
}

/* Active link style */
.is-active-link {
  font-weight: bold;
  color: #007bff;
}

/* end tocbot */

/*///////////////////////////////////////////////////////////////////////////////////////////*/

header {
    font: ;
    display: flex;
    justify-content: space-between; /* 改为左右分布 */
    align-items: center;
    height: 4rem;
    padding: 0 2rem; /* 增加左右内边距 */
}

.profile {
    display: flex;
    align-items: center;
    gap: 0.3rem; /* 头像和昵称之间的间距 */
}

.avatar {
    width: 2rem;
    height: 2rem;
    /*border-radius: 50%;*/ /* 圆形头像 */
    object-fit: cover; /* 保持图片比例 */
}

.nickname {
    color: #ddd;
    font-weight: bold;
}


header nav{
  min-width: 20rem;
}

header li{
  display: inline-block;
  margin: 0 0.8rem;
}

header li a{
    color: #ddd;
}

.fluid{
/*  margin-top: 6rem;*/
  margin: 3rem auto 2rem;
  max-width: 50rem;
  padding: .25rem;
}

img {
  margin: 0.7rem auto;
}


/* ---- footnotes -------------------------------------------- */

  sup::before{
    content:"[";
  }

  sup::after{
    content:"]";
  }

  .footnote-backref::before{
    content:"[";
  }
  
  .footnote-backref::after{
    content:"]";
  }

  .footnote-backref{
    color: #bbb;
  }


/* ---- table ------------------------------------------------ */

  table {
      width: 90%;
      margin: 1.5rem auto;
      border-collapse: collapse;
  /*    border-left: 1px white solid;*/
  /*    border-right: 1px white solid;*/
  /*    box-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);*/

  }

  th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #444444;
  }

  th {
      background-color: #222222;
      color: #ffffff;
  }

  tr:nth-child(even) {
      background-color: #282828;
  }


/* ---- giscus ----------------------------------------------- */
  .giscus{
    
  }


/* ---- scroll bar ------------------------------------------- */

  /* firefox并不支持，但以下主要也是为了调整chrome系的浏览器的滚动条 */
  
  ::-webkit-scrollbar {
      width: 0.5rem; /* 垂直滚动条的宽度 */
      height: 0.5rem; /* 水平滚动条的高度 */
    
  }
  /* 鼠标悬浮在滚动条上的颜色变化 */
  ::-webkit-scrollbar-thumb:hover {
      background: #555; /* 鼠标悬浮时的颜色 */
  }

  ::-webkit-scrollbar-thumb {
      background: #888; /* 手柄颜色 */
          border-radius: 6px;
  }
```
注意：
- 模板引擎使用python的chervon
- 再次提醒，从cache.json生成的时光轴的页面主要内容content将作为**部分模板**来给chervon进行处理。除了content之外，其它的部分模板将存放在config.yaml所指示的路径partials_dir中，应该一起读取以供chervon处理。
- 如果有date为空的记录，这些记录在页面中就展示为“创建时间丢失”这一分类之中。

请你帮我用python写一下这个模块。

### 时间轴页面的模板
请帮我生成一个博客时光轴页面的模板（模板风格使用chervon这种）

要求：
- `<h1>``<h2>`等的h标签要给时间，比如“2025年”，“5月”这样标记时间的东西。然后博文的标题或者跳转链接之类的不应该使用h标签

风格你可以大致参考我的风格：
```css
/*//////////////////////////////////////////////////////////////////////////////////////*/

/* begin retro (https://github.com/markdowncss/retro) */

code {
  /* 行内代码 */
  margin: 0 0.2rem;
  padding: 0 0.3rem;
  background-color: #303841;
  border-radius: 0.25rem;
/*  border: 1px solid #505050;*/
}

pre,
pre code {
  font-family: Source Code Pro,DejaVu Sans Mono,Ubuntu Mono,Anonymous Pro,Droid Sans Mono,Menlo,Monaco,Consolas,Inconsolata,Courier,monospace,PingFang SC,Microsoft YaHei,sans-serif;

/* ---- print ---------------------------------------------------------------------------------------------*/

@media print {
  *,
  *:before,
  *:after {
    background: transparent !important;
    color: #000 !important;
    box-shadow: none !important;
    text-shadow: none !important;
  }

  a[href]:after {
    content: " (" attr(href) ")";
  }

  abbr[title]:after {
    content: " (" attr(title) ")";
  }

  a[href^="#"]:after,
  a[href^="javascript:"]:after {
    content: "";
  }

  pre,
  blockquote {
    border: 1px solid #999;
    page-break-inside: avoid;
  }

  thead {
    display: table-header-group;
  }

  tr,
  img {
    page-break-inside: avoid;
  }

  img {
    max-width: 100% !important;
  }

  p,
  h2,
  h3 {
    orphans: 3;
    widows: 3;
  }

  h2,
  h3 {
    page-break-after: avoid;
  }
}
/* ---- end print ---------------------------------------------------------------------------------------------*/

a {
/*  color: #01ff70;*/
  text-decoration: none;
  color: #45a9f9;
/*  font-family: "宋体", "SimSun", cursive;*/
  font-family: "宋体", "SimSun";
}

a:hover,
a:focus,
a:active {
/*  color: #2ecc40;*/
  color: #62bfff;
}


.retro-no-decoration {
  text-decoration: none;
}

html {
  font-size: 12px;
  transition: all 0.35s ease 0.1s;
}

@media screen and (min-width: 32rem) and (max-width: 48rem) {
  html {
    font-size: 14px;
  }
}

@media screen and (min-width: 48rem) {
  html {
    font-size: 16px;
  }
}

p,
.retro-p {
  font-size: 1rem;
  letter-spacing: 0.1rem; 
/*  margin-bottom: 1.3rem;*/
}

h1,
.retro-h1,
h2,
.retro-h2,
h3,
.retro-h3,
h4,
.retro-h4 {
  margin: 1.414rem 0 .5rem;
  font-weight: inherit;
  line-height: 1.42;
  font-family: "宋体", "SimSun", sans-serif;
  color: #fff;
}

h1,
.retro-h1 {
  margin-top: 0;
  margin-bottom: 0;
/*  margin-bottom: 4rem;*/
  font-size: 3.88rem;
}

h2,
.retro-h2 {
  font-size: 2.78rem;
}

h3,
.retro-h3 {
  font-size: 1.9rem;
}

h4,
.retro-h4 {
  font-size: 1.414rem;
}

h5,
.retro-h5 {
  font-size: 1.121rem;
}

h6,
.retro-h6 {
  font-size: .88rem;
}

small,
.retro-small {
  font-size: .707em;
}

/* https://github.com/mrmrs/fluidity */

img,
canvas,
iframe,
video,
svg,
select,
textarea {
  max-width: 100%;
}

html,
body {
/*  background-color: #222;*/
  background-color: #22262a;
  min-height: 100%;
}

body {
  color: #bbb;
  font-family: Helvetica Neue, NotoSansHans-Regular,AvenirNext-Regular,arial,Hiragino Sans GB,Microsoft Yahei,WenQuanYi Micro Hei,serif;
/*  font-family: system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;*/
  line-height: 1.45;
}

pre {
/*  background-color: #333;*/
/*  background-color: #393f46;*/
}

blockquote {
/*  border-left: 3px solid #01ff70;*/
  border-left: 3px solid #45a9f9;
  background-color: #66666619;
  padding: 0.1rem 1rem;
/*  font-size: smaller;*/
/*  font-family: "楷体", "KaiTi", cursive;*/
/*  font-style: italic;*/
}

/* end retro */


/*///////////////////////////////////////////////////////////////////////////////////////////*/

/* begin left-sidebar */

.left-sidebar{
  position: fixed;
  top: 50%; /* Adjust as per your layout */
  left: 0%; /* This will position the div on the left side */
  transform: translate(0, -50%); /* Center vertically based on its own height */

  display: flex;

}

.toc-toggle{
  width: 20px;
  height: 3.2rem;
  background-color: #45a9f977;
  border-radius: 0 5px 5px 0;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
/*  margin-top: 0.4rem;*/
  cursor: pointer;
}

.toc-toggle:hover{
  background-color: #45a9f9aa;
}

.toc-hidden{
  margin-left: -17.5rem;  /*  此值等于.toc.width + .toc.padding-right */
}

/* end left-sidebar */


/* begin tocbot */

.toc {
  background-color: #313438;
  padding: 1rem 0;
  padding-right: 0.5rem;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
  overflow-y: auto;
  border-radius: 0 0.1rem 0.5rem 0;
  max-height: calc(100vh - 40px); 
  width: 17rem;
  transition: all 0.45s ease;
}

.toc a{
  color: white;
}

.toc-list{
  padding-left: 1.9rem;
}

/* Style for the main list items */
.toc-list-item {
  list-style: none;
/*  margin-bottom: 8px;*/
}

/* Style for the links */
.toc-link {
  text-decoration: none;
  color: #333;
  display: block;
  padding: 5px 5px 5px 10px;
  margin-right: 10px;
  border-radius: 3px;
  transition: background-color 0.3s ease;
}

/* Hover effect for the links */
.toc-link:hover {
  background-color: #e0e0e02e;
}

/* Active link style */
.is-active-link {
  font-weight: bold;
  color: #007bff;
}

/* end tocbot */

/*///////////////////////////////////////////////////////////////////////////////////////////*/

header {
    font: ;
    display: flex;
    justify-content: space-between; /* 改为左右分布 */
    align-items: center;
    height: 4rem;
    padding: 0 2rem; /* 增加左右内边距 */
}

.profile {
    display: flex;
    align-items: center;
    gap: 0.3rem; /* 头像和昵称之间的间距 */
}

.avatar {
    width: 2rem;
    height: 2rem;
    /*border-radius: 50%;*/ /* 圆形头像 */
    object-fit: cover; /* 保持图片比例 */
}

.nickname {
    color: #ddd;
    font-weight: bold;
}


header nav{
  min-width: 20rem;
}

header li{
  display: inline-block;
  margin: 0 0.8rem;
}

header li a{
    color: #ddd;
}

.fluid{
/*  margin-top: 6rem;*/
  margin: 3rem auto 2rem;
  max-width: 50rem;
  padding: .25rem;
}

img {
  margin: 0.7rem auto;
}


/* ---- footnotes -------------------------------------------- */

  sup::before{
    content:"[";
  }

  sup::after{
    content:"]";
  }

  .footnote-backref::before{
    content:"[";
  }
  
  .footnote-backref::after{
    content:"]";
  }

  .footnote-backref{
    color: #bbb;
  }


/* ---- table ------------------------------------------------ */

  table {
      width: 90%;
      margin: 1.5rem auto;
      border-collapse: collapse;
  /*    border-left: 1px white solid;*/
  /*    border-right: 1px white solid;*/
  /*    box-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);*/

  }

  th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #444444;
  }

  th {
      background-color: #222222;
      color: #ffffff;
  }

  tr:nth-child(even) {
      background-color: #282828;
  }


/* ---- giscus ----------------------------------------------- */
  .giscus{
    
  }


/* ---- scroll bar ------------------------------------------- */

  /* firefox并不支持，但以下主要也是为了调整chrome系的浏览器的滚动条 */
  
  ::-webkit-scrollbar {
      width: 0.5rem; /* 垂直滚动条的宽度 */
      height: 0.5rem; /* 水平滚动条的高度 */
    
  }
  /* 鼠标悬浮在滚动条上的颜色变化 */
  ::-webkit-scrollbar-thumb:hover {
      background: #555; /* 鼠标悬浮时的颜色 */
  }

  ::-webkit-scrollbar-thumb {
      background: #888; /* 手柄颜色 */
          border-radius: 6px;
  }

```

### cache.json转化为timeline模板可接受的格式
cache.json（内容如下）：
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
将这样的json格式文件转化为下面的格式。

```json
{
  "years": [
    {
      "year": "2025",
      "months": [
        {
          "month": "5",
          "timelineItems": [
            {
              "position": "left",
              "date": "2025年5月15日",
              "link": "post1.html",
              "title": "探索人工智能的未来发展",
              "description": "这篇文章探讨了人工智能技术的未来发展趋势，包括机器学习、自然语言处理和计算机视觉等领域的最新进展。"
            },
            {
              "position": "right",
              "date": "2025年5月10日",
              "link": "post2.html",
              "title": "Web开发最佳实践",
              "description": "分享一些现代Web开发的最佳实践，包括响应式设计、性能优化和可访问性等方面的建议。"
            }
          ]
        },
        {
          "month": "4",
          "timelineItems": [
            {
              "position": "left",
              "date": "2025年4月25日",
              "link": "post3.html",
              "title": "深入理解CSS Grid布局",
              "description": "详细介绍CSS Grid布局系统的使用方法，包括基本概念、常用属性和实际应用案例。"
            },
            {
              "position": "right",
              "date": "2025年4月18日",
              "link": "post4.html",
              "title": "JavaScript ES2025新特性预览",
              "description": "探索即将到来的JavaScript ES2025标准中的新特性和语法改进，帮助开发者提前准备。"
            }
          ]
        }
      ]
    },
    {
      "year": "2024",
      "months": [
        {
          "month": "12",
          "timelineItems": [
            {
              "position": "left",
              "date": "2024年12月20日",
              "link": "post5.html",
              "title": "年度技术回顾与展望",
              "description": "回顾2024年最重要的技术发展，并对2025年的技术趋势进行预测和展望。"
            },
            {
              "position": "right",
              "date": "2024年12月5日",
              "link": "post6.html",
              "title": "构建高效的前端工作流",
              "description": "分享如何建立高效的前端开发工作流，包括工具选择、自动化流程和团队协作等方面的经验。"
            }
          ]
        }
      ]
    }
  ],
  "miss_date": [
    {
      "position": "left",
      "date": "2014年5月21日",
      "link": "post7.html",
      "title": "不知道",
      "description": "介介"
    },
    {
      "position": "right",
      "date": "2020年4月5日",
      "link": "post8.html",
      "title": "你深情",
      "description": "写成了我们"
    }
  ]
}
```
时间以cache.json中的`date`字段为准。
如果`date`为空，那么就放在`miss_date`这么一个集合中。

至于`position`这个字段，那么就一个左一个右就行了。

然后日期解析的话，要能够支持以下格式：
"%y/%m/%d/%H:%M",  # 24/9/24/19:05
"%Y/%m/%d/%H:%M",  # 2024/9/24/19:05
"%Y/%m/%d",         # 2024/9/24
"%y/%m/%d",         # 24/9/24
"%Y-%m-%d",         # 2024-9-24

用python编写一个这个模板，结果不需要保存到外寸，打印字符串即可

### timeline扩展
打开一个模板文件，然后