---
title: 给博客整一个新的访问量统计工具：GoatCounter
date: 25-10-18 19:56
has_toc: false
---

不太记得从谁的博客里看到的[这个工具](https://www.goatcounter.com/)了，当时看介绍就觉得不错。像百度、谷歌这类互联网巨头它们其实都有这类网站统计工具，但你知道的，巨头拿你的数据做什么可没人知道。虽然说其实我这种小站也没什么好担心的，但是就是不能助纣为虐(●'◡'●)。这个网站的介绍也正是击中了这一要害：
> GoatCounter is an open source web analytics platform available as a free donation-supported hosted service or self-hosted app. It aims to offer easy to use and meaningful privacy-friendly web analytics as an alternative to Google Analytics or Matomo.
> 
> GoatCounter是一款开源网络分析平台，提供两种使用方式：基于捐赠的免费托管服务，或可自行部署的应用程序。该平台致力于提供直观易用、数据洞察精准的隐私友好型网络分析解决方案，旨在成为Google Analytics和Matomo的替代选择。

GoatCounter开源免费，还能自托管，无疑是消除了用户对隐私问题的顾虑。对于我这种小站来说可能不是那么有所谓，我看重的还是他的简单易用。创建自己的账户之后，只需要在自己的网站中添加一段html标签就完事了。
```html
<script data-goatcounter="https://yoursite.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
```
接着就可以到自己的后台静静地等待数据增加了🤭（现实是只有我自己的访问）。

![图片加载失败：goatcounter后台]({{img_url}}Snipaste_2025-10-18_19-49-13_compressed.jpg)

[我之前搞的评论系统Valine](v1.0.3改版日志——评论系统的选择.html#我的选择Valine)其实也有访问统计功能。不过它需要在第三方云平台部署代码，搞起来比较麻烦。相比之下，GoatCounter真的是十分的方便。而且今天下午测试的时候，发现Valine的访问量统计好像是有些bug，很多次访问都没被统计进去。

更让人欣喜的是，GoatCounter也能通过api获取单独某个页面的访问量，于是就可以在页面里显示这个访问量了。而且方法也很简单，同样是加一点html标签就行了。
```html
<script>
    window.goatcounter.visit_count({append: 'body'})
</script>
<script data-goatcounter="https://你的域名.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script>
```
这样的话会在`body`标签的最后生成一个html标签：
```html
<body>
    <!-- 你页面的所有其他内容 -->

    <!-- GoatCounter 计数器会添加在这里 -->
    <div class="gcvc">
        Views for this page: 1,234 stats by GoatCounter
    </div>
</body>
```
不过除了访问量，还有些英文，这些是固定的。

还好除了这种方式还有个直接返回json的api能够拿到纯粹的访问量数字。
例如直接在浏览器地址栏输入`https://code-pigeon.goatcounter.com/counter/blog/html/index.html.json`，那么就能得到：
```json
{
  "count": "4",
  "count_unique": "4"
}
```
`"count": "4"`就是我的主页的访问量了。

有了这个api，在页面的任何角落放一个访问量也是轻而易举了。
```js
// 使用 GoatCounter 的 JSON API
var t = setInterval(function() {
    if (window.goatcounter) {
        clearInterval(t);
        
        // 获取当前页面路径
        let path = window.goatcounter.get_data()['p'];
        
        // 获取访问量数据
        fetch('https://你的域名.goatcounter.com/counter/' + encodeURIComponent(path) + '.json')
            .then(r => r.json())
            .then(data => {
                document.getElementById('my-counter').textContent = data.count;
            })
            .catch(err => {
                document.getElementById('my-counter').textContent = '0';
            });
    }
}, 100);
```
说了这么多，其实我现在在文末显示的还是Valine的访问统计，有空了再更新成GoatCounter吧哈哈。

散会！