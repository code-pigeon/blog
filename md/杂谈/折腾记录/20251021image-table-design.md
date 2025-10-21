---
title: 图片容灾备份：为预防图床跑路，我给博客做了一个图片表
date: 25-10-21 13:42
---

## 引子
我看过太多的博客，博文里的图片链接全都是失效的。我大概心里能猜出是些什么原因，比如图床倒了？或者图片不小心误删了？

这些对我来说都是不可接受的。所以从建立博客之初，我就同时在云端和本地都存了图片。这么做不仅可以预防图床跑路，也意味着我的这个静态博客，可以做到完完全全不联网也能在本地正常浏览。

可能大家有些迷糊，图片又放本地和放云端，那岂不是两条图片链接，而在博客里一张图片显然只能放一个链接，难不成同一张图片放两次？

其实不是的，我在我之前的博文[图床的选择](图床的选择.html)中有提到我对图床的要求。我想要那种上传了之后还能保持原来文件名的图床。也就是说，本地图片`D:/test.jpg`上传到图床之后的名字能够是`https://imgbed.com/test.jpg`。这样我在自己的博客里大可以把图片链接写成：
```markdown
![test图片](D:/test.jpg)
```
然后我在本地就能正常用本地的路径显示图片。

那如果是用网络访问我的博客呢？难道大家看到的图片都是从我的电脑上获取的吗？

当然不是，我用js写了点代码，让这个图片加载失败的时候，就把图片名前面的`D:/`替换成图床的路径`https://imgbed.com/`，这样在网络上访问我的博客，就可以通过图床获取到图片。

实现起来很简单，几行代码的事情：
```js
// 定义备用路径
const fallbackBaseUrl = "https://imgbed.com/"; // 备用路径
// 监听所有 .fluid 下的 img 标签
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('div.fluid img');
    images.forEach(function(img) {
        img.addEventListener('error', function() {
            const currentSrc = img.src;
            // 如果当前已经是备用路径，则移除 src（避免无限循环）
            if (currentSrc.includes(fallbackBaseUrl)) {
                img.removeAttribute('src'); // 仅显示 alt
                return;
            }
            // 替换主路径为备用路径（保留文件名）
            const fileName = currentSrc.split('/').pop(); // 提取文件名（如 "test.jpg"）
            const newSrc = fallbackBaseUrl + fileName;    // 拼接备用路径
            img.src = newSrc; // 尝试加载备用图
        });
    });
});
```

不过这种方案要求图床上传图片之后，返回的图片路径仍保留图片的文件名。这种要求十分苛刻，类似sm.ms、路过图床这一类公共图床，都是不具备这种特点的。而像七牛云、又拍云这一类云服务平台，虽然符合这个需求，但是他们不会给用户一个稳定的图片链接前缀，需要用户用自己的域名去生成这个图片链接。但我又不想搞域名，因为搞域名就意味着实名认证、备案之类的乱七八糟的事，我要是能容忍，就不会只把博客放在github上了。

所以剩下的选择就只有cloudflare这一类海外的产商，我确实一开始也是[用cloudflare当作图床](20250421cloudflare-as-image-host.html)的，但是前两天发现cloudflare在国内的访问速度十分感人，是比GitHub还慢的存在，基本就等于不可访问。

于是我又开始想办法了……只能妥协选择那些公共图床了，那如何解决图片上传之后链接不会保持图片名的问题呢……

## 图片表的诞生
计算机领域有句名言叫做
> 计算机科学领域的任何问题，都可以通过增加一个间接中间层来解决。

我面临的这个问题也能用类似的办法解决。既然图片的链接可能很多样，没什么规律，那我干脆就不放图片的链接了，而是加一层，给每一张图片都设置一个id，然后可以通过id寻找到图片的所有链接，就像下面这样：
```yaml
图片1: 
	- D:/test1.jpg
	- https://imgbed.com/jkljkljkl
	- https://code-pigeon.github.io/blog/this-is-a-image
图片2: 
	- D:/image/好康的.png
	- https://imgbed.com/abcabcefg
	- https://code-pigeon.github.io/blog/this-is-another-image
```

然后我在博客里就可以写

{{=( )=}}
```html
<img  data-url="{{图片1}}"  />
```

这里的`{{`和`}}`之间的内容，就通过模板引擎去图片表中找到对应的值，替换为图片实际的各个链接，替换之后就类似下面这样：
```html
<img  data-url="D:/test1.jpg;https://imgbed.com/jkljkljkl;https://code-pigeon.github.io/blog/this-is-a-image"  />
```
在这里，各个链接被通过`;`进行分隔。（这么分隔好像是html标签的自定义数据的一种标准做法）

(=< >=)

然后再用js代码把`data-url`中的数据挨个作为`img`标签的`src`进行尝试加载就行啦。（测试代码放在[最后面](#备份js加载img中的data-url作为src测试代码)，给自己备份一下）

> 理论上直接用markdown写`![test]({{图片1}})`应该也没什么问题，不过这样，图片的`src`就存着多个数据，虽然反正能通过js把图片的src变成其中的一个，自己觉得不算是一种很好的做法吧。

<=( )=>

当然这样一个图片表，肯定也不是自己手动维护的。我还另外写了一个python程序，能够上传到各个不同图床之后更新图片表，并且返回图片的链接，基本上功能和PicGo相似吧，只不过多了一个维护图片表的功能。这个程序就是堆工作量，没什么新鲜玩意儿，就按下不表了。

## 图片表真的有必要吗
大家应该也能看到，既然`<img  data-url="{{图片1}}"  />`最后还是会变成`<img  data-url="D:/test1.jpg;https://imgbed.com/jkljkljkl;https://code-pigeon.github.io/blog/this-is-a-image"  />`，那为什么不直接用后者，而要多此一举搞个图片表呢。

(={{ }}=)

如果使用后者，那么假如真的有某个图床绷掉了，这些图片链接散落在各个博文中，修改起来必定十分的麻烦。假如把链接都统一放在同一张图片表中，那么批量修改起来将会十分的方便。

其实即使我能给出这样的理由，在设计之初还是犹豫了，毕竟额外维护一个图片表是很大的代价。不过问了deepseek，它夸赞我这是一个非常明智的工程实践设计，于是受到鼓舞的我也就顺势把这个想法落实下来了。

---

## 备份：js加载img中的data-url作为src测试代码
```html
<img data-url="img1.ico;https://bilibili.com/favicon.ico;image1.png" />
<img data-url="img1.ico;image1.png;https://baidu.com/favicon.ico" />
<img data-url="img1.ico;image1.png" />



<script>
const img = document.querySelector('img');
const urls = img.dataset.url.split(';');
console.log(urls); // ["favicon.ico", "img1.ico", "image1.png"]

img.src = urls[0];

</script>

<script>
	function loadImagesWithFallback() {
	    const images = document.querySelectorAll('img[data-url]');
	    
	    images.forEach(img => {
	        const urls = img.getAttribute('data-url').split(';');
	        let currentIndex = 0;
	        
	        function loadNext() {
	            if (currentIndex >= urls.length) {
	                console.warn('All image URLs failed to load:', urls);
	                return;
	            }
	            
	            const url = urls[currentIndex].trim();
	            if (!url) {
	                currentIndex++;
	                loadNext();
	                return;
	            }
	            
	            const testImg = new Image();
	            testImg.onload = () => {
	                img.src = url;
	                img.removeAttribute('data-url');
	            };
	            testImg.onerror = () => {
	                currentIndex++;
	                loadNext();
	            };
	            testImg.src = url;
	        }
	        
	        loadNext();
	    });
	}

	// 页面加载完成后执行
	document.addEventListener('DOMContentLoaded', loadImagesWithFallback);

	// 如果需要在动态添加图片后也能处理，可以导出这个函数
	window.loadImagesWithFallback = loadImagesWithFallback;
</script>
```