# 白嫖weibo的视频资源记
首次编辑：2024/8/19/23:36
最后编辑：2024/8/21/01:16

因为搞了个[简易视频壁纸命令行程序](简单的视频桌面壁纸实现.html)，所以要开始收集视频了。

在微博上白嫖视频，最简单的方式当然是用现成的工具。

- [sucps.com](http://sucps.com)：需要关注公众号。
- [下载狗](https://www.xiazaitool.com)：有每日下载次数限额。

这两个工具都可以下载。

~~不过作为一个程序员~~，总是好奇背后的原理。而且我也想学会自己白嫖，就不用求人了。

## 探索过程
了解html页面的话，肯定最先想到的是在浏览器里按下`ctrl + shift + C`，然后点击目标视频，找到对应的元素，然后寻找视频的url。
在微博里，视频的标签如下：
```html
<video data-v-560f3af5="" class="wbpv-tech" playsinline="playsinline" webkit-playsinline="true" x5-playsinline="true" x5-video-player-type="h5" x5-video-player-fullscreen="false" id="wbpv_video_455_html5_api" tabindex="-1" preload="meta" src="//f.video.weibocdn.com/o0/g4Cr4fYjlx083Ic6jb3i010412018X9d0E010.mp4?label=mp4_1080p&amp;template=1920x1080.25.0&amp;media_id=4877088713539648&amp;tp=8x8A3El:YTkl0eM8&amp;us=0&amp;ori=1&amp;bf=4&amp;ot=h&amp;ps=3lckmu&amp;uid=6xTbLC&amp;ab=,8143-g0,8013-g0,3601-g19,7598-g0&amp;Expires=1724082476&amp;ssig=K4%2BrYO4AG7&amp;KID=unistore,video"></video>
```
虽然乱七八糟的，但是还是可以找到我们想要的url，也就是`src="`后面的内容，在这里是
```
//f.video.weibocdn.com/o0/g4Cr4fYjlx083Ic6jb3i010412018X9d0E010.mp4?label=mp4_1080p&amp;template=1920x1080.25.0&amp;media_id=4877088713539648&amp;tp=8x8A3El:YTkl0eM8&amp;us=0&amp;ori=1&amp;bf=4&amp;ot=h&amp;ps=3lckmu&amp;uid=6xTbLC&amp;ab=,8143-g0,8013-g0,3601-g19,7598-g0&amp;Expires=1724082476&amp;ssig=K4%2BrYO4AG7&amp;KID=unistore,video
```
于是我们可以在浏览器的输入框中输入这个url，然后不出意外的话，就要看到403了。

我后来了解到这是“防盗链”机制搞的鬼。

> 24/8/21/00:51 注：
> 但后来发现又不是，而是[动态签名](#动态签名)机制。

### 防盗链？
比如我在我的博客里引用了微博的视频，那么访客进入我的网站之后，`video`标签就会向微博发送请求以获取这个视频，于是微博用自己的服务器对这个请求进行了处理，但结果却返回到了我的博客里。换句话说微博成了为了打工的了，万恶的资本家们肯定不会这么好心啊，所以这些资源的拥有者们往往会采用某些技术手段来防止像我这种盗用url的家伙，这就是所谓的“防盗链”。

技术毕竟是人创造的，有人创造，就会有人知道怎么破解。
在网上看到的比较多的说，为了防盗链，这些网站会在网站中使用`referrer`标识来记录这个请求资源的请求是不是来自自家的域名，于是咱们可以在自己的网页中写上html标签：
```html
<meta content="never" name="referrer">
```
来关闭防盗链。
也有人说这么写：
```html
<meta content="no-referrer" name="referrer">
```

于是我腰杆子瞬间直了起来，兴冲冲写了个html文件：
```html

<!DOCTYPE html>
<html>
<head>
	<meta content="never" name="referrer">
	<title>test</title>
</head>
<body>
	<video src="https://f.video.weibocdn.com/o0/i2M3bZF3lx083v7CjStq01041201SKSl0E010.mp4?label=mp4_1080p&template=1920x1080.25.0&media_id=4874117988679687&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=4&ot=h&ps=3lckmu&uid=6xTbLC&ab=,8143-g0,8013-g0,3601-g19,7598-g0&Expires=1724074020&ssig=OgFaj88BL2&KID=unistore,video"></video>
</body>
</html>
```
然后不出意外的话，意外就来了，结果视频还是没出现。按下F12打开控制台，发现还是403了。

于是瞬间又不牛逼了。可能是微博的程序员们比较屌，还有什么更高级的技术用在这了。没办法，还是斗不过资本家，这个问题就等以后有兴趣再研究了吧……

### 动态签名
24/8/20/22:42

很快我就又“有兴趣”了，昨晚看了一篇[介绍防盗链机制的博客](https://juejin.cn/post/7079705713781506079)，里面提到“防盗链”这个技术一般用于A网站防止B网站在B网站中盗用A网站的媒体资源链接，而不防止用户自己在浏览器中输入资源链接。也就是说，如果我知道了`video`标签的`src`，并在新的标签页打开这个链接，“防盗链”一般不会阻止我们的这种做法。

但很显然，微博的这个视频链接无法在新的标签页里直接打开，所以微博应该使用了什么别的技术来防止我们这一行为。

于是我开始关注到“动态签名”这一技术。

我做了一个实验，找到微博页面中的某个视频的url，然后刷新，再观察一下这个url，再刷新再观察。三个url的结果如下：
```
//f.video.weibocdn.com/o0/e5RdvHVOlx083RT5on8k01041200XuFT0E010.mp4?label=mp4_720p&template=1280x720.25.0&media_id=4879290869940459&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=4&ot=h&lp=00003LyjHy&ps=mZ6WB&uid=6xTbLC&ab=,8143-g0,3601-g34,8013-g0,3601-g19,7598-g0&Expires=1724168333&ssig=UO%2BJuMQMI2&KID=unistore,video

//f.video.weibocdn.com/o0/e5RdvHVOlx083RT5on8k01041200XuFT0E010.mp4?label=mp4_720p&template=1280x720.25.0&media_id=4879290869940459&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=4&ot=h&lp=00003LyjHy&ps=mZ6WB&uid=6xTbLC&ab=,8143-g0,3601-g34,8013-g0,3601-g19,7598-g0&Expires=1724168175&ssig=apcURe9QKk&KID=unistore,video 

//f.video.weibocdn.com/o0/e5RdvHVOlx083RT5on8k01041200XuFT0E010.mp4?label=mp4_720p&template=1280x720.25.0&media_id=4879290869940459&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=4&ot=h&lp=00003LyjHy&ps=mZ6WB&uid=6xTbLC&ab=,8143-g0,3601-g34,8013-g0,3601-g19,7598-g0&Expires=1724168443&ssig=OuQwCLS01J&KID=unistore,video
```
仔细观察就会发现，url中的其它部分都相同，除了参数`Expires`和`ssig`。“expire”是过期的意思，后面跟的那个很明显是一个时间戳，大概代表这个链接的失效时间。而至于`ssig`，可能跟签名“signature”有关。

三次访问微博的同一个页面，同一个视频的url的这两个参数却是不同的。所以我想可以得出一个结论，在请求视频的url发送给微博的服务器后，服务器可能会验证这两个参数是否合法，从而决定是否返回视频资源。

所以如果要在独立的标签页中的打开这个视频链接，我们可能得想办法模拟微博页面自己的行为，发送一个“请求视频url”的请求，于是返回的这个url中就带有合法的`Expires`和`ssig`，这样就能够通过这个合法的url请求微博服务器返回对应的视频。

于是我按下F12，打开网络，搜索了一下`ssig`，果然找到了这个“请求视频url”的请求。它的样子是这样的：
```
https://weibo.com/ajax/statuses/mymblog?uid=7822545252&page=1&feature=0
```
这应该是请求获得某个具体用户的动态所用的链接，从`ajax`可以看出它是一个异步请求，用于动态加载页面中局部的内容。

因为这个url请求的是“某个用户的动态”，所以它返回的内容不止是一个视频，所以如果想要从返回的内容中找到想要的视频，可能就得花点时间在寻找上了。

但其实如果只是简单地想要下载视频，根本用不了这么麻烦……

> 关于类似的技术，还可以参阅[API接口签名(防重放攻击)](https://juejin.cn/post/6983864029550739463)

### 通过编辑video标签下载视频
浏览器本身是支持用户下载浏览器中显示的视频的，只需要右击视频，就会有保存视频的选项。但这些个类似微博的网站，右键之后只会弹出“复制视频地址”，这就是它们防止别人下载视频的最初级方法。

右击鼠标，浏览器是会出现默认的菜单栏的。但是在微博视频为啥出现的是“复制视频地址”？不用像，微博的程序员们自定义了右键处理事件覆盖掉了浏览器的默认右键处理事件。

让视频被右击时依旧触发浏览器的默认右击处理事件，不就可以下载视频了？

于是我略加思索，看了一下那个又臭又长的`video`标签，突然有了一个想法：微博的程序员不会是通过css类来处理右击事件的吧？
于是我打开微博，`ctrl + shift + C`选中了一个视频，找到`video`标签，右击，选择“编辑为html”，然后把出了`src`之外的属性统统删除：
```html
<video src="https://f.video.weibocdn.com/o0/i2M3bZF3lx083v7CjStq01041201SKSl0E010.mp4?label=mp4_1080p&template=1920x1080.25.0&media_id=4874117988679687&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=4&ot=h&ps=3lckmu&uid=6xTbLC&ab=,8143-g0,8013-g0,3601-g19,7598-g0&Expires=1724074020&ssig=OgFaj88BL2&KID=unistore,video"></video>
```
![图片：成功实现保存视频](../media/image/article/Snipaste_2024-08-20_00-18-01.png)

哈哈哈哈！

正当我欣喜若狂，拿着下载好的视频和用那两个网站下载好的视频进行对比时，我突然傻眼了。
左边是我自己下载的，右边是用那两个网站下载的。
![图片：对比1](../media/image/article/Snipaste_2024-08-20_00-22-14.png)
大小的差距更是离谱。
![图片：对比2](../media/image/article/Snipaste_2024-08-20_00-22-30.png)
即使我把视频质量调整到1080p，还是比从那两个网站下载的的质量要低得多。

而且我自己下载的还是有水印的。而网站下载的没有。

而且我后来发现，如果用“复制视频地址”的那个地址打开视频，就是可以直接右键下载的🥲。

### 神秘的url
于是我去看了一下那两个网站解析出来的视频的url。
譬如对于某个视频，有如下的一系列url：
```
1、右键“复制视频地址”得到的：http://t.cn/A6CIU9pi

2、输入链接“1”之后，浏览器显示的url：https://weibo.com/tv/show/1034:4874117988679687

3、video标签的url：//f.video.weibocdn.com/o0/i2M3bZF3lx083v7CjStq01041201SKSl0E010.mp4?label=mp4_1080p&template=1920x1080.25.0&media_id=4874117988679687&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=4&ot=h&ps=3lckmu&uid=3ZoTIp&ab=,8143-g0,8013-g0,3601-g19,7598-g0&Expires=1724088955&ssig=FzQh5JRx5z&KID=unistore,video

4、两个网站解析出来的url：https://ad.video.weibocdn.com/o0/EMnNHuurlx083v7bUpLO01041207zwdK0E030?Expires=1724085252&ssig=ne2EcJZIkc&KID=unistore,video
```
> 注：解析出来的url似乎是有时限的。写完时“4”已经无法打开了（403）。

对于“3”这个url其实是比较好理解的，在域名之后，`i2M3bZF3lx083v7CjStq01041201SKSl0E010.mp4`表示请求的文件名，再后面的都是一些请求参数。

对于“4”这个神秘的url，同样在域名之后参数之前的`EMnNHuurlx083v7bUpLO01041207zwdK0E030`，可能也是一个文件的文件名，只是不带后缀名而已。

但问题在于，如何通过“1”或“2”或“3”中的这些标识了视频资源的各种id（例如“1”的`A6CIU9pi`、“2”的4874117988679687，“3”的`i2M3bZF3lx083v7CjStq01041201SKSl0E010`）来得到用于请求“4”的`EMnNHuurlx083v7bUpLO01041207zwdK0E030`呢。

在微博视频的页面中，按下F12，在“网络”选项卡中寻找`EMnNHuurlx083v7bUpLO01041207zwdK0E030`，很遗憾，没有任何痕迹。但那两个网站却能够通过“1”、“2”、“3”或者它们的任意排列组合来找到这个神秘的字符串……

我目前的水平没办法想出其中奥秘，只能说，也许这两个网站的作者在微博后端工作过。

> 24/8/21/00:54 注：
> 现在想想，这个奇怪的字符串必然就是服务器发来的，而且服务器不仅仅是发这个神秘的字符串，而是……整个url都是服务器发来的。
> 关键在于怎么找到“能让服务器返回这个视频url”的url。

### url编码加密技术
24/8/21/00:58

在知道有[动态签名](#动态签名)这回事之后，我就继续在开发者窗口里探索，然后在网络包中看到了一个奇怪的链接：
```
sinaweibo://video/vvs?mid=4879496988329450&object_id=1034:4879290869940459&url_type=39&object_type=video&pos=1
```
这个链接是无法直接在浏览器里打开的，后来在一篇文章[^1]里，我认识到这种链接是一种经过加密的url。但是这种链接会在页面的js代码中解码成真正的url，所以想要白嫖只能去研究页面里的js代码了。
> 我试了一下，发现里面的代码上万行，果断放弃了，代码放在sublime里都好卡。
> 
> 根据文章中的说法，应该还有些网站会在这个代码中使用自己的视频播放器，那样的话，即使解码得到真正的url，那个url也是不能直接播放的，这有点恐怖的啊，不过想想就觉得工程量很大，应该不会有很多页面使用这种办法。

## 参考
[^1]: 思否（Segment Fault），Jack，[在线视频常见加密方式及安全性透析](https://segmentfault.com/a/1190000014632981)
