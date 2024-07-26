# 【python笔记】弱引用weakref

*参考书籍*：
《深度学习入门——自制框架》[日]斋藤康毅 步骤17.4 weakref模块

强引用会出现循环引用的情况
```python
class obj():
	pass

a = obj()  # 使用赋值运算，引用计数加1
b = obj()
c = obj()
# 执行到这里，a、b、c的引用计数都为1

a.b = b  # 被对象强引用，引用计数加1
b.c = c
c.a = a
# 执行到这里，a、b、c的引用计数都为2
```
这样a、b、c三个对象的引用计数都为2，即使执行`a = b = c = None`，引用计数仍然为1，a、b、c都不会被释放（计数为0时，python会自动释放内存空间）
```python
import weakref 

class obj():
	pass

a = obj()
b = weakref.ref(a)

print(f"b：{b}")
print(f"a：{a}")
print("使用b()可以访问b引用的对象")

print(f"b() = {b()}")

a = None
print("====== 运行 a = None 后 ======")
print(f"b：{b}")
```
可以发现运行`a = None`之后，b引用的对象变成`dead`了，表明引用的对象已经被删除。
此时再运行`print(b())`，输出会变成`None`。