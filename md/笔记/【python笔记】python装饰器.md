# python装饰器
首次编辑：24/3/8/23:09  
最后编辑：24/3/8/23:21

## 形如@dec(param1 = 1, param2 = 2)的装饰器
```python
def decorator(param1 = 1, param2 = 2):
# 装饰器接收两个参数，默认值分别为1和2
	def wrapper2(func):
		def wrapper1(*args, **kwargs):
			print("-----------------------------------------------------------")
			print("############# 此时被装饰的函数还未执行 #############")
			print(" ")
			# 在这里可以访问和处理传入的关键字参数
			print(f"\t参数1={param1}，参数2={param2}。")
			func(*args, **kwargs)  # 执行被装饰函数
			print(" ")
			print("############# 此时被装饰的函数已经执行完了 #############") # 被装饰的函数执行完后执行这里
			print("-----------------------------------------------------------")
		return wrapper1
	return wrapper2


@decorator(param2 = "3")
def func_being_decorated():
    """Docstring"""
    print("\t[Warning] 被装饰的函数执行中……")
```
输出为：
```comment
-----------------------------------------------------------
############# 此时被装饰的函数还未执行 #############

        参数1=1，参数2=3。
        [Warning] 被装饰的函数执行中……

############# 此时被装饰的函数已经执行完了 #############
-----------------------------------------------------------
```