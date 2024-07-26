# 【python笔记】contextlib，自定义with语句
*参考书籍*：
《深度学习入门——自制框架》[日]斋藤康毅 步骤18.5 使用with语句切换

## with语法
python中的`with`语句，用于自动进行后处理。
如文件读写：
```python
with open('sample.txt', 'w') as f:
  f.write('hello sb!')
```
这段代码等价于
```python
f = open('sample.txt', 'w')
f.write('hello sb!')
f.close()
```
可以看到`with`其实就是帮助程序员自动将打开的文件关闭。

## contextlib.contextmanager装饰器
使用contextlib中的contextmanager装饰器，就可以实现自定义的`with`语句了：
```python
import contextlib 

@contextlib.contextmanager
def test():
	print('start')  # 预处理
	try:
		yield
	finally:
		print('done')  # 后处理

# 简单理解为将with中的代码搬到test()中的yield处，然后执行test()
with test():
	print('process...')
```
输出：
```
start
process...
done
```