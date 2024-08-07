# C语言中返回局部变量指针的探究
首次编辑：24/3/19/20:26  
最后编辑：24/3/19/

## 简短的故事
学汇编的时候，知道了在函数结束之后，函数栈应该是会被清理的。由于局部变量位于函数栈中，所以理论上一个函数若返回它的局部变量的地址是不可行的，这个地址中的数据会被清理。
所以如果如下定义一个函数会发生警告：
```c
void *test(){
	int x;
    x = 3;
	return &x;
}
// warning: function returns address of local variable [-Wreturn-local-addr]
```
然而神奇的是，如果我像下面这样写，警告就消失了：
```c
void *test(){
	int x;
    x = 3;
    int *p = &x;
	return p;
}
```
而如果再在main函数当中输出`*p`，也会发现确实等于3。一度导致我纠结了很久。

后来才知道，两种方式都是不安全的，只是第二种写法编译器探测不到这个潜在的问题而已。
