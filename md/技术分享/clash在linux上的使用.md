# clash在linux上的使用
首次编辑：24/12/03/16:14
最后编辑：24/12/04/17:03

在Windows上有带图形界面的clash for windows，但是clash Linux端的好像没有带图形化界面的，只有命令行。我一开始回避了这个问题，只在windows上用clash，但是最近因为想给博客升级，有时候上github都上不去，Linux端科学上网的需求还是无法回避，所以就学习了一下如何在Linux上使用命令行版本的clash。

## 环境
Ubuntu20.04 x86-64

## 正文
### 命令行版clash的下载和安装
**下载**
现在网上可以找到很多clash的下载[^clash下载]，clash也有很多版本，我使用的是clash-verge[^clash-verge]，下载地址为[https://github.com/zzzgydi/clash-verge/releases](https://github.com/zzzgydi/clash-verge/releases)。

> **clash的版本问题**
> 
> clash好像有很多个版本，好像clash的作者在23年底被请去喝茶了，github仓库也被删了，不过好像有个不愿意透露姓名的小黑子[^clash-rev]说他接过了维护clash的重任，但我看了一下，23年底更新了一两次之后就没有继续更新了。
> 
> 现存的版本我看到有叫clash的，有叫clash-verge的（就是我用的版本），小黑子的版本叫clash-rev，知乎上有人说有个叫Mihomo[^《Clash-/-Mihomo-装配指南-(Ubuntu)》]的……
> 而clash for windows对应的是哪个我也不太清楚，或者只是为这些个版本中的某个编写了用户界面。

我下的是`clash-verge_1.3.8_amd64.deb`，因为`AppImage`运行起来好像会缺东西，而`.deb`可以借助apt来同时下载缺的东西。

**安装**
```bash
sudo apt install path/to/clash-verge_1.3.8_amd64.deb
```
测试安装是否成功
```bash
$ clash -v
Clash 2023.08.17 linux amd64 with go1.21.0 Thu Aug 17 15:07:25 UTC 2023
```

### 配置
一般配置文件（`config.yaml`）会放在`~/.config/clash/`路径下。

**通过订阅链接获得配置文件**
在命令行输入：
```bash
$ cd ~/.config/clash/ 
$ wget -O config.yaml <订阅链接>
```
将`<订阅链接>`替换为实际的订阅链接。

**直接复制配置文件内容**
也可以在clash for windows中，复制配置文件的内容，然后在`~/.config/clash/`路径下，新建一个`config.yaml`，然后将复制的内容粘贴上来。

### 设置网络代理
在正式使用之前，还需要设置一下网络代理。
回到桌面，右键依次点击“设置”、“网络”、“网络代理最右边的按钮”、“手动”，然后在下面的选项中填入
|项目名称|第一栏|第二栏|
|--|--|--|
|HTTP代理|127.0.0.1|7890|
|HTTPS代理|127.0.0.1|7890|
|Socks主机|127.0.0.1|7891|
|忽略主机|localhost, 127.0.0.0/8, ::1|

> 这样做有个问题，就是在关闭clash之后，再访问网址，会出现“代理服务器拒绝连接”。
> 
> 我尝试过使用命令行来设置网络代理（即`export http_proxy=http://127.0.0.1:7890`），这样子当命令行窗口关闭之后，网络代理就又失效了，不过问题是，这样子设置，好像网络代理只在当前命令行窗口生效，在浏览器的眼里仍然是没有代理的。
> 
> 所以解决办法应该只能是一直开着clash了，如果想像clash for windows一样有个关闭代理的方法，可以直接把节点切换为`DIRECT`（如何切换节点参考[下文](#切换节点)）。

### 启动
在命令行下输入：
```bash
$ clash
```
就可以启动了，正常情况下启动后将输出运行日志。


### 切换节点
切换节点需要使用到clash提供的api[^使用Clash-API切换节点][^clash知识库][^clash.Rev-Docs][^clash.gitbook.io]。

clash开启之后会监听9090端口，这时候在浏览器网址框中输入本地ip`127.0.0.1:9090`能够看到clash返回了一个json数据`hello: "clash"`。
> 我使用的clash-verge是没有ui界面的，不过我看很多教程中[^eaglebear2002.github.io][^大哥云教程合集]，在浏览器输入的不是本地ip，而是` http://clash.razord.top/#/proxies`，然后返回的是一个类似clash for windows的ui界面。感觉应该是个不同的clash版本。

参考clash api，要切换节点需要向`127.0.0.1:9090`发送POST请求，可以在命令行下使用curl来实现：
```bash
curl -X PUT -H "Content-Type: application/json" -d '{"name":"<节点名>"}' http://127.0.0.1:9090/proxies/<代理组名>
```
这里的`<节点名>`和`<代理组名>`要参考自己的配置文件（`config.yaml`），一般在配置文件中会有如下的内容：
```yaml
proxy-groups:
  - name: <代理组名>
    type: select
    proxies:
      - <节点名1>
      - <节点名2>
      - DIRECT
```

#### 使得切换节点立即生效
但是节点的切换并不会立即生效，而是需要关闭clash，重新启动，或者再发送下面的一个请求：
```bash
curl "http://127.0.0.1:9090/configs" -X PUT -d '{"path": "", "payload": ""}'
```

---


<!-- clash下载 -->
[^clash下载]:[clash知识库](https://clash.wiki/) 
[^《如何在-Clash-for-Linux上配置服务》]: Helium-Network，[《如何在 Clash for Linux上配置服务》](https://www.henet.uk/posts/%E5%A6%82%E4%BD%95%E5%9C%A8-clash-for-linux%E4%B8%8A%E9%85%8D%E7%BD%AE%E6%9C%8D%E5%8A%A1/)
[^clash]: github，doreamon-design，[clash](https://github.com/doreamon-design/clash/releases)
[^clash-for-linux-install]: github，nelvko，[clash-for-linux-install](https://github.com/nelvko/clash-for-linux-install?tab=readme-ov-file#%E5%BC%95%E7%94%A8)
[^clash-verge]: github，zzzgydi，[clash-verge](https://github.com/zzzgydi/clash-verge/releases)
[^《Clash-/-Mihomo-装配指南-(Ubuntu)》]: 知乎，Arkcia，[《Clash / Mihomo 装配指南 (Ubuntu)》](https://zhuanlan.zhihu.com/p/690371003)
[^clash-rev]: github，MerlinKodo，[clash-rev](https://github.com/MerlinKodo/clash-rev/releases)

<!-- api参考 -->
[^clash知识库]: [clash知识库](https://clash.wiki/runtime/external-controller.html)
[^clash.Rev-Docs]: Clash.Rev——不愿透露姓名的小黑子维护的新Clash项目，[Clash.Rev Docs](https://merlinkodo.github.io/Clash-Rev-Doc/api/)
[^clash.gitbook.io]: [https://clash.gitbook.io/doc](https://clash.gitbook.io/doc/restful-api)

<!-- 切换代理 -->
 [^使用Clash-API切换节点]: Kronos，[使用Clash-API切换节点](https://sakronos.github.io/Note/2021/03/06/%E4%BD%BF%E7%94%A8Clash-APIj%E5%88%87%E6%8D%A2%E8%8A%82%E7%82%B9/)

<!-- 安装指南 -->
<!-- 有ui的 -->
[^eaglebear2002.github.io]:[EagleBear2002 的博客，Ubuntu 22.04 安装 Clash](https://eaglebear2002.github.io/%E6%8A%80%E6%9C%AF%E7%A7%91%E6%99%AE/Ubuntu%2022.04%20%E5%AE%89%E8%A3%85%20Clash/)
[^大哥云教程合集]: 大哥云教程合集，[《Ubuntu 使用 Clash For Linux 客户端教程》](https://doc.6bc.net/article/35/)

<!-- 无ui的 -->
<!-- 知乎，Arkcia，[《Clash / Mihomo 装配指南 (Ubuntu)》](https://zhuanlan.zhihu.com/p/690371003) -->
