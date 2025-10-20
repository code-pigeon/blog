---
title: 我也用cloudflare R2来做图床了
date: 25-04-21 19:16
---

在[之前的博客中](图床的选择.html)，我提到了我对图床的要求。找了不少免费图床，最后只有一家图床满足我的要求。

> 复述一下我对图床的要求：我希望图床能够保留文件的文件名，而不是随机给我另外生成一个。（这样能够方便我实现备用图床的机制，详见我之前的博客[图床的选择](图床的选择.html)

今天逛博客的时候又看到了别人用大名鼎鼎的cloudflare R2来做图床的，不知道为什么记忆错乱，老是以为自己试过这个cloudflare了，其实并没有，于是今天尝试了一下，没想到这么简单，而且它也满足我对图床的要求（就是图片的链接有点丑）。

## cloudflare R2的作用
简单来说就两个：

1. 存储文件；
2. 提供文件的公共访问链接（于是可以在博客上引用这些文件）；

这不就是天生当图床的种吗。

## cloudflare R2的免费额度
cloudflare R2的好处在于它有一定的免费额度。

| 存储空间 | A 类操作（上传/删除）| B 类操作（访问文件链接） |
|----------|-------------------|-------------------------|
| 10 GB/月 | 100 万次请求/月    | 1000 万次请求/月         |


这里的存储空间的收费方式可能有些迷惑，举个例子方便理解：

比如说存12GB的图片，存了半个月就删除了，那么实际上额度的消耗是`12GB * 0.5个月 = 6GB`，所以依然是不用付费的。
但如果12GB图片存了一整个月，那额度的消耗是`12GB * 1个月 = 12GB`，此时就只能含泪交钱了。

对于其它的两种操作，对于个人博客来说应该也是绰绰有余了。

## 如何使用cloudflare R2作为图床？
首先是注册cloudflare账号，这就不多说了。

然后找到左侧的`R2 Object Storage`，点击之后会让你先填付款方式（以便超过免费使用额度了它可以自动恰米\[乐\])，可以是银行卡，不过右上角也提供了PayPal的选项，这个就根据大家的具体情况去填了。下面还需要填写一些个人的信息，尚且不清楚不填真实信息有没有什么影响，不过反正我没填真实的也成功了。

<img data-url="{{image_table.cloudflare-as-image-host-开通cloudflare R2}}" title="开通cloudflare R2" alt="图片加载失败：开通cloudflare R2"/>

成功添加付款方式之后，会进入overview页面，此时就可以创建自己的图床了。在右边有个蓝色的`Create bucket`按钮，点击创建。

<img data-url="{{image_table.cloudflare-as-image-host-创建bucket}}" title="创建bucket" alt="图片加载失败：创建bucket"/>

起个自己想要的名字，然后其它选项都保持默认就行了。

创建成功后进入自己的bucket，然后就可以上传自己的文件了。可以直接拖拽自己的图片到页面里，也可在中间点击`select from computer`。（可以同时上传多个文件）

<img data-url="{{image_table.cloudflare-as-image-host-上传文件}}" title="上传文件" alt="图片加载失败：上传文件"/>

成功之后应该可以看到自己上传的文件出现在列表中。

<img data-url="{{image_table.cloudflare-as-image-host-上传文件成功}}" title="上传文件成功" alt="图片加载失败：上传文件成功"/>

这时候还需要最后一步才能让自己的博客能够引用文件的链接，那就是打开公共访问权限。

具体来说，点击`Settings`，拖动到下面会看到`Public access`，在第二项的`R2.dev subdomain`右边的红色按钮`Allow Access`处点击，然后输入提示词即可。

<img data-url="{{image_table.cloudflare-as-image-host-开启公共访问}}" title="开启公共访问" alt="图片加载失败：开启公共访问"/>

此时再回到自己的bucket文件列表，点击文件名，就可以看到自己的文件的链接了。

<img data-url="{{image_table.cloudflare-as-image-host-得到图片链接}}" title="得到图片链接" alt="图片加载失败：得到图片链接"/>

> 当然如果你有自己的域名就可以在开启公共访问权限那一步，点击`Connect Domain`，这样就能够自定义自己的图片链接。

这个文件链接的前缀是固定的，只要属于同一个bucket，那么只有文件名是不同的，而且cloudflare不会修改上传的文件名，你电脑里是叫啥名，上传之后就是啥名（这点深得我心）。


最基础的用法基本就是这样了，网上很多其它教程涉及到什么picgo之类的，好像就是为了实现上传之后自动压缩、调整图片尺寸什么的（类似专门做图床的网站的效果），我没有这种需求，所以就不搞那么麻烦了。

最后列一下我看到的其它实现cloudflare R2搭建图床的教程：

- [Serve static assets with Cloudflare R2](https://brettweir.com/blog/static-assets-cloudflare-r2/)
- 嘰嘰乞乞，[（試圖）一勞永逸的博客圖片管理解決方案 ](https://www.gigigatgat.ca/posts/cloudflare-r2-image-hosting/)