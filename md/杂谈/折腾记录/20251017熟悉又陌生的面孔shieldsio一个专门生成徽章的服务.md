---
title: 熟悉又陌生的面孔：Shields.io（一个专门生成徽章的服务）
date: 25-10-17 13:19
updated: 25-10-18 13:31
---

> 今天又发现了一个第三方网站可以更简单地查询和使用徽章[substats.swo.moe](https://substats.swo.moe/)（更新于：25-10-18 13:31）

## 啥是Shields.io徽章
[![B站](https://img.shields.io/badge/dynamic/json?url=https://api.bilibili.com/x/relation/stat?vmid=516728425&query=data.follower&label=乌鸦有想法&color=00A1D6&logo=bilibili)](https://space.bilibili.com/516728425)

对于这个东西，我想做对编程比较熟悉的人应该太眼熟了。很多GitHub项目的README文档中都会出现这种东西。

虽然说见了很多次这个东西，但是也是直到今天想美化一下首页里我的社媒的跳转链接的时候，才终于知道这是个啥。

deepseek说，这是[![Shields.io](https://img.shields.io/badge/shields.io-000?logo=shieldsdotio&logoColor=white&style=flat-square)](https://shields.io)这个网站提供的功能，这玩意儿的正式名称叫做“徽章”。

在一些项目中，或者博客中，使用Shields.io提供的徽章已经是一种非常常见的做法了。很多大平台，比如B站、抖音之类的都在Shields.io创建了属于自己的徽章。

![B站](https://img.shields.io/badge/bilibili-00A1D6?style=for-the-badge&logo=bilibili&logoColor=white)

当然对于我们个人也是可以创建属于自己的徽章的，而且这玩意儿居然还是免费的。

那么要如何在自己的博客中使用这些徽章呢？


## 徽章的使用
虽然只是刚刚接触这玩意儿，不过感觉已经看了个七七八八了。

```
https://img.shields.io/badge/乌鸦有想法-000000
```
如果在浏览器的地址栏输入上面的链接，那么将会出现如下东西：
![徽章：乌鸦有想法](https://img.shields.io/badge/乌鸦有想法-000000)

聪明的你肯定看出来了：

- `https://img.shields.io`是shield的域名；
- `badge`是基本样式，“badge”意为徽章；
- `乌鸦有想法`是要显示的文字；
- `000000`是颜色代码，这里也可以直接写颜色名，如red、blue等；

所以如果想换成红色背景就可以写
```
https://img.shields.io/badge/乌鸦有想法-red
```
效果为：
![徽章：红底的乌鸦有想法](https://img.shields.io/badge/乌鸦有想法-red)

那怎么在博客中用呢？

如果是使用markdown写博客，那么很好办：
```markdown
![徽章：红底的乌鸦有想法](https://img.shields.io/badge/乌鸦有想法-red)
```
也可以用纯html：
```html
<img src="https://img.shields.io/badge/乌鸦有想法-red" />
```

其实就是插入图片的链接就行了。

当然如果想要让这个徽章成为可以点击的标签，那么只需要在图片外面套一个超链接就行了。
markdown：
```markdown
[![徽章：红底的乌鸦有想法](https://img.shields.io/badge/乌鸦有想法-red)](https://space.bilibili.com/516728425)
```
html：
```html
<a href="https://space.bilibili.com/516728425">
	<img src="https://img.shields.io/badge/乌鸦有想法-red" />
</a>
```

另外，徽章实际上还支持两段文本
```
https://img.shields.io/badge/乌鸦有想法-赛博乌鸦-yellow
```
效果如下：
![两段文本](https://img.shields.io/badge/乌鸦有想法-赛博乌鸦-yellow)

### 使用知名平台的logo
知名的平台基本都有在shields.io创建自己的logo，所以可以直接在链接中引用这些logo。以B站举个例：
```
https://img.shields.io/badge/B站?logo=bilibili
```
加上请求参数`logo=bilibili`即可获得B站logo（其它平台也一样，比如github，那么就换成`logo=github`）

效果如下：
![B站徽章](https://img.shields.io/badge/B站-000000?logo=bilibili)

当然这个logo的颜色还可以改变，只需要在后面加上参数`logoColor=颜色代码`就可以了，比如`https://img.shields.io/badge/B站?logo=bilibili&logoColor=222`，效果如下：

![B站徽章](https://img.shields.io/badge/B站-000000?logo=bilibili&logoColor=fff)


### 在链接中使用api
[![B站](https://img.shields.io/badge/dynamic/json?url=https://api.bilibili.com/x/relation/stat?vmid=516728425&query=data.follower&label=乌鸦有想法&color=00A1D6&logo=bilibili)](https://space.bilibili.com/516728425)
有没有好奇后面那串数字是什么意义？

那其实是我的B站粉丝数。

这种徽章其实还有个专门的名字，叫动态徽章，因为我的粉丝数可能会随时变化，这个徽章就可以同步更新。

所以这类徽章的链接都中会有个`dynamic`（意为动态）。让我们看看上面那个徽章的链接长什么样：
```
https://img.shields.io/badge/dynamic/json?url=https://api.bilibili.com/x/relation/stat?vmid=516728425&query=data.follower&label=乌鸦有想法&color=00A1D6&logo=bilibili
```
后面的`label`、`color`、`logo`其实就是之前说的徽章文本、颜色、logo。

前面的`json?url=https://api.bilibili.com/x/relation/stat?vmid=516728425&query=data.follower`才是动态徽章的重点。

像B站的话，它会提供一些开放的api，比如`https://api.bilibili.com/x/relation/stat?vmid=516728425`这个api，如果直接在浏览器地址栏里输入，那么将会返回这样的东西：
```json
{
    "code": 0,
    "message": "0",
    "ttl": 1,
    "data": {
        "mid": 516728425,
        "following": 510,
        "whisper": 0,
        "black": 0,
        "follower": 447
    }
}
```
对网络有了解的朋友应该知道这是json格式的返回信息，所以shields.io就通过`query=data.follower`这个额外的参数去定位到返回数据中的`follower`这个数据，它表示的是B站用户（在这里是我）的粉丝量。

像这种从api中获得的数据，就是“动态徽章”中“动态”的来源了。

互联网中除了json格式，xml格式也是一种数据传递比较常用的格式，那么在使用shields.io动态徽章时，就可以把上面链接中的`json`换成`xml`了，像这样：
```
https://img.shields.io/badge/dynamic/xml?url=（此处放置api链接）&query=（此处放置筛选路径）
```

至于这些api怎么找，其实我也不是自己找的，2025年了嘛，问AI就行了。

---

我对shields.io徽章的了解大概就这些了，其它的什么神奇的用法和功能，就等需要时再聊吧。

再会！
