# 关于Flask中View function mapping is overwriting an existing endpoint function
首次编辑：24/3/10/11:03  
最后编辑：24/3/10/11:57

## 引子
### 背景
本来是在写个人网站，以前的代码中，几乎每个视图函数都有类似于：
```python
@app.route("/")
def index():
	try:
		return send_file("index.html")
	except FileNotFoundError as e:
		abort(404)
```
我就在想怎么能减少重复书写同样的代码，于是想到了装饰器。
```python
def not_found(func):
	def wrapper(*args, **kwargs):
		print("进入装饰器")
		try:
			func(*args, **kwargs)
		except:
			print("失败！文件未找到")
			return "失败！文件未找到"
	return wrapper


@app.route("/", methods=["GET"])
@not_found
def index():
	return send_file("index.html")
```
写到这里还没什么问题，但当我再加一个视图函数，同样也使用了这个`@not_found`装饰器的时候，报错出现了。
```
AssertionError: View function mapping is overwriting an existing endpoint function: wrapper
```

### 解决办法
解决办法网上很容易搜到，
1. 第一种是给装饰器加上`@wraps()`
```python
from functools import wraps

def not_found(func):
	@wraps(func)  # 新增的代码
	def wrapper(*args, **kwargs):
		# 省略装饰器内容
	return wrapper


@app.route("/", methods=["GET"])
@not_found
def index():
	return send_file("index.html")


@app.route("/data", methods=["GET"])
@not_found
def data():
	return send_file("data.html")
```

2. 第二种是在`@app.route()`中加上`endpoint`参数
```python
def not_found(func):
	@wraps(func)  # 新增的代码
	def wrapper(*args, **kwargs):
		# 省略装饰器内容
	return wrapper


@app.route("/", methods=["GET"], endpoint="data")
@not_found
def index():
	return send_file("index.html")


@app.route("/data", methods=["GET"], endpoint="data")
@not_found
def data():
	return send_file("data.html")
```

## 为什么会出现这个错误？
### 最简单的情况
要引发这个报错，最简单的方法是定义两个不同的路由，但它们拥有相同的视图函数名：
```python
'''
	路由1：“/”，视图函数名为“index”
	路由2：“/data”，视图函数名为“index”
'''

@app.route("/", methods=["GET"])
def index():
	return send_file("index.html")

@app.route("/data", methods=["GET"])
def index():
	return send_file("data.html")
```
出现这个报错是因为，路由是通过`endpoint`这个变量来区分视图函数的，而默认情况下，`endpoint`的值就是视图函数的名字。
在上面这种情况下，两个视图函数的名字都是`index`，所以路由“/”的endpoint默认为`index`，当路由“/data”也要用默认的视图函数名`index`来作为`endpoint`的值时，发现这个值已经被路由“/”占用了，因此报错。

这种情况最简单，只需要把路由“/data”的视图函数名改成其它名字就行了。

可这并不是我遇到的情况，所以引出了下面的问题。

### 为什么不同的视图函数名加了装饰器之后也会出现这个报错？
#### 先补一点关于装饰器的知识
要想明白这个问题，首先要懂一点装饰器的知识。
我们先看个例子：
```python
def decorator(func):
	def wrapper(*args, **kwargs):
		print(f"{decorator.__name__}开始执行")
		func(*args, **kwargs)
		print(f"{decorator.__name__}执行完毕")
	return wrapper

@decorator
def func():
	print(f"{func.__name__}开始执行")
	print(f"{func.__name__}执行完毕")

func()
```
输出为：
```
decorator开始执行
wrapper开始执行
wrapper执行完毕
decorator执行完毕
```

可以看到，在func函数中，输出了自己的函数名`func.__name__`，但终端打印出来的却不是“func”，而是“wrapper”。
也就说，被装饰器装饰过的函数，其函数名（`.__name__`）其实就已经变成了装饰器的内层函数名（在本例中为`wrapper`）。

于是答案呼之欲出了。

#### 答案

在上面的例子中：
```python
def not_found(func):
	def wrapper(*args, **kwargs):
		# 省略装饰器内容
	return wrapper


@app.route("/", methods=["GET"])
@not_found
def index():
	return send_file("index.html")


@app.route("/data", methods=["GET"])
@not_found
def data():
	return send_file("data.html")
```
从代码执行顺序来看，`@app.route`装饰了一个被`@not_found`装饰过的`index`函数，而因为被装饰过的`index`函数的函数名（`__name__`属性）已经变成了`wrapper`，所以实际上“/”路由的`endpoint`是`wrapper`。
下面的“/data”路由也是同理，所以`@app.route("/data")`这个路由装饰的是被`@not_found`装饰过的`data`函数，所以路由“/data”的`endpoint`也会是`wrapper`，但这个`endpoint`值已经被路由“/”占用了，因此报错：`View function mapping is overwriting an existing endpoint function: wrapper`。

#### 再回头看看为什么解决办法会奏效
直接在路由中手动加`endpoint`的办法就不用多说了，非常直观。

而在装饰器中加上`@wraps`又是如何奏效的呢。
前面说到，被装饰器装饰过的函数，其函数名（`__name__`属性）就不是函数本身的名字了，而是装饰器内层函数（其实就是装饰器返回的函数）的名字（`__name__`属性），而`@wraps`的作用就是让被装饰的函数的名字仍然保持为其本身的名字（参考[Python 使用wraps和不使用wraps的装饰器的区别？](https://www.zhihu.com/question/46808546)），这样`@app.route`再装饰被`@not_found`装饰过的视图函数，其`endpoint`的默认取得的值就不再是`wrapper`，而是视图函数本身的名字了，此时只要视图函数的名字本身不重复，就不会出现这个报错。

## 后记
可能会有些小伙伴说，搞那么麻烦，直接把`@app.route`和`@not_found`的顺序调换一下，这样`@app.route`装饰到的就是视图函数本身了，就不会有什么重复的`endpoint`了。
确实是这个样子，但这两个装饰器的顺序调换照成的影响不止这一点，实际上在开头引子中，`@not_found`装饰器放在最外层是完全不起作用的（目前我还没研究明白具体原因）。
所以还是根据实际开发中的需求来决定吧，这或许也是个好办法。