# C++笔记
## 奇异递归模板模式(Curiously Recurring Template Pattern)
[参考链接](https://zhuanlan.zhihu.com/p/54945314)
简单说就是把子类作为父类的模板参数。

## 静态多态性返回可变和不可变对象
这源于我在看奇异递归模板模式(Curiously Recurring Template Pattern)时看到的例子：
```c++
struct VectorBase
{
	T& underlying() { return static_cast<T&>(*this); }
	T const& underlying() const { return static_cast<T const&>(*this); }
	// ...
}
```
不熟悉肯定是看懵了，两个成员函数的名字一模一样，区别只在于`const`。

> ChatGPT：
在使用 underlying() 函数时，编译器会根据调用方式的不同来选择调用哪个函数。
如果调用对象是一个非常量对象（即可修改的对象），则会调用 T& underlying() 函数，返回的是一个 T& 引用类型，可以直接对其进行修改操作。
如果调用对象是一个常量对象，则会调用 T const& underlying() const 函数，返回的是一个 const T& 引用类型，表示该对象是只读的。

然后又给了个例子：
```c++
class VectorBase {
public:
    int x;
    int& underlying() { return x; }
    int const& underlying() const { return x; }
};

int main() {
    VectorBase vb{ 1 };
    auto& ref = vb.underlying(); // 调用 T& underlying()
    std::cout << ref << std::endl; // 输出 1
    ref = 2;
    std::cout << vb.x << std::endl; // 输出 2

    const VectorBase cvb{ 3 };
    auto const& cref = cvb.underlying(); // 调用 T const& underlying() const
    std::cout << cref << std::endl; // 输出 3
    // cref = 4; // 编译错误，无法修改只读对象
    return 0;
}

```