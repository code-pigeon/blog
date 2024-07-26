# python多个装饰器执行的顺序
首次编辑：24/3/9/11:06  
最后编辑：24/3/10/10:59

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


@not_found
@app.route("/", methods=["GET"])
def index():
	return send_file("index.html")
```
正当我得意洋洋启动服务器测试时，却发现当文件不存在时，装饰器中的语句根本不会执行，程序会直接崩溃。

### 不小心解决了
正当我觉得心灰意冷，打算另辟蹊径的时候，我尝试调换了一下`@not_found`和`@app.route`这两个装饰器的位置，结果就成功了……
很显然这和装饰器的执行顺序有关。

## 一个函数被多个装饰器装饰，装饰器执行的顺序如何？
于是我写了两个装饰器，
```python
def dec1(func):
	def wrapper(*args, **kwargs):
		print(f"{dec1.__name__}开始执行")
		func(*args, **kwargs)
		print(f"{dec1.__name__}执行完毕")
	return wrapper

def dec2(func):
	def wrapper(*args, **kwargs):
		print(f"{dec2.__name__}开始执行")
		func(*args, **kwargs)
		print(f"{dec2.__name__}执行完毕")
	return wrapper

@dec2
@dec1
def func():
	print(f"{func.__name__}开始执行")
	print(f"{func.__name__}执行完毕")

if __name__ == '__main__':
	func()
```
输出结果为：
```
dec2开始执行
dec1开始执行
wrapper开始执行
wrapper执行完毕
dec1执行完毕
dec2执行完毕
```
这表示装饰器的执行顺序是从上到下的，也可以说是从外向内的。
