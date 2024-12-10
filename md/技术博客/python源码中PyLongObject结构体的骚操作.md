# python源码中PyLongObject结构体的骚操作
首次编辑：2024/11/24/17:23
最后编辑：2024/11/25/12:32

这两天在考虑升级自己的模板引擎，给写博文的markdown添加一下头部的元数据。现在元数据的解析器也找好了，问题是这个解析器真的只解析，不管存储，于是我需要解决存储元数据的问题。因为这些数据可能会有不同的类型，所以还需要能够存储不同类型的数据（虽然现在其实没有这么细致的需求，但是为了防止以后哪天突然就有这个需求了）。

在考虑的时候还想着直接把模板引擎的控制语句（比如`{% for item in items%}`）也用Lua来实现，顺便头部的元数据也直接用Lua来写，这样就可以直接用Lua来写头部的元数据了。不过试了一下发现好像模板的控制语句用Lua的解析不太方便，就放弃了。

自己瞎想不太好，我还是想借鉴一下现实案例，第一个想到的就是python（其实是因为我只看看过一点python的源代码），于是就去看了python的源代码，然后就发现了PyLongObject里的一些奇怪设计。

## 正文
> 【注】
> 
> 1. 正文中的python源码版本为3.8；
> 2. 由于python的源码仓库名称为cpython（可能是表明python是C写的？），所以下文都称python源码为cpython。

在进入主题之前，需要先了解一下python中的一切变量在cpython中都是什么样子的。这需要我们先了解两个cpython中的结构体：`PyObject`和`PyVarObject`。

### cpython中所有Python变量类型的父类PyObject
python中的一切变量类型的对象在源码的实现中都是一个由`PyObject`扩展而来的结构体。

例如python中的`float`类型变量在cpython中的表示是`PyFloatObject`结构体。

`PyObject`包含了一个python变量所需要的信息，比如引用计数（用于垃圾回收），类型对象（保存着类型的名称、方法等）：
```c
// include/object.h

typedef struct _object {
    _PyObject_HEAD_EXTRA			// （一个宏，不影响本文叙述，按下不表）
    Py_ssize_t ob_refcnt;			// 引用计数 
    struct _typeobject *ob_type;	// 类型对象结构体
} PyObject;
```

而`PyFloatObject`其实仅仅只比`PyObject`多了一个数据域而已：
```c
// include/object.h
#define PyObject_HEAD PyObject ob_base;

// include/floatobject.h
typedef struct{
    PyObject_HEAD
    double ob_fval;		// 数据域
} PyFloatObject;
```

某种意义上说，这种代码的编写方式是在C语言中模拟继承，所以可以说，在cpython中，`PyObject`是一切python变量类型的父类。

### cpython中所有python可变长变量类型的父类PyVarObject
Var可能是“variable（可变的）”的意思，`PyVarObject`结构体可以表示所有的python可变长的变量类型，例如`list`。`PyVarObject`实际上也是由`PyObject`扩展而来，它仅仅比`PyObject`多了一个表示长度的数据域。
```c
// include/object.h

typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size; /* 表示变量长度的数据域 */
} PyVarObject;
```

那么在python中可变长的类型，如`list`，它在cpython中对应的结构体`PyListObject`，又是如何从`PyVarObject`扩展而来的呢？类似`PyFloatObject`之于`PyObject`，`PyListObject`也是由`PyVarObject`加上自己的数据域组成：
```c
// include/object.h
#define PyObject_VAR_HEAD	PyVarObject ob_base;

// include/listobject.h
typedef struct {
    PyObject_VAR_HEAD

    /* list类型的数据域 */
    PyObject **ob_item;		// 指向列表存储的数据指针
    Py_ssize_t allocated;	// 表示已经分配的内存空间大小
} PyListObject;
```

### PyLongObject
python中的整型变量，在cpython中由结构体`PyLongObject`表示。

很出乎意料的是，`PyLongObject`是由`PyVarObject`扩展而来的，而不是`PyObject`，也就是说，在cpython眼里，整型数据居然是“可变长”的（为什么加引号呢？后文会给出答案）。

其实是因为python需要满足对大整型数据（例如一个有100位有效数字的整型数字，这个数字用64bit也不够表示）的需求。
> 对于大整型的表示的实现，不是本文的重点，在此按下不表。
`PyLongObject`的定义如下：
```c
// include/object.h
#define PyObject_VAR_HEAD	PyVarObject ob_base;

// include/longobject.h
typedef struct _longobject PyLongObject;

// include/longintrepr.h
struct _longobject{
	PyObject_VAR_HEAD
	digit ob_digit[1];
};
```
这里的`digit`是一个无符号整型类型。`ob_digit`数组存放的正是整型变量的值，假如`obj_digit`中的内容是`[11, 22, 33]`，那么它所表示的整型就是`11*(2^30)^0 + 22*(2^30)^1 + 33*(2^30)^2`（为什么幂次是30？这是cpython中指定的，我尚不明白为啥不是32）。

但奇怪的是，这个`ob_digit`没有我想像中的那样，声明为一个指针，而是声明为了数组，而且还居然直接声明了一个固定的长度`1`，既然固定了长度，又怎么“变长”呢？

可能有人会说，数组不就是指针吗。

### 重温C语言中数组和指针的区别
“数组和指针的区别”是个很经典的问题。

可以这么理解：`int *p`只声明了一个指针，但`int p[100]`声明了指针的同时（实际上这个指针并不存在，但`p`确实可以当指针用，只不过无法修改），还在当前栈中开辟了可以容纳100个`int`的空间，然后将指针指向了这个空间。

但是如果是在结构体中声明数组和指针，又会有什么区别呢。

其实本质差不多，可以直接把结构体看成一个栈。

### 在结构体中声明数组的妙用
说了这么久，才终于到了今天的主题。

回顾刚刚我们的问题，为什么
1. 在`PyLongObject`中不用`digit *ob_digit;`而要用`digit ob_digit[1];`？
2. 而且只声明了`1`的长度，这样要如何“变长”呢？

第一个问题其实很好解答，因为如果是`digit *ob_digit`这样的声明，除了要多存储一个指针之外，因为此时`ob_digit`指针还没有赋值，想要赋值还得额外去内存堆中动态申请一块空间出来，然后再给指针赋值，完了之后，在要释放的时候还需要手动去释放这块的申请的空间，十分麻烦。但如果是声明为数组，那么在结构体被释放的同时，数组空间也会同时被释放（因为这个数组其实就是结构体的一部分），省去了手动管理内存空间的麻烦。

第二个问题，如何“变长”呢？

如果直接在代码中写：
```c
PyLongObject py_long_object;
```
或
```c
PyLongObject *py_long_object = (PyLongObject*)malloc(sizeof(PyLongObject));
```
那这个`long`类型就恐怕真的只是一个数据位而已了。实际上在cpython中并不会用到这种简单的内存分配方式。cpython有一套完整的内存分配体系，虽然很复杂（所以本文中不讨论），但其实给`PyLongObject`分配内存的思路非常简单。

在`malloc`的时候，需要指定要分配的空间大小，这个时候就不要老老实实的分配大小为`sizeof(PyLongObject)`的空间了，可以多开点空间，比如
```c
PyLongObject *py_long_object = (PyLongObject*)malloc(sizeof(PyLongObject) + 123*sizeof(digit));
```
这样就多分配了123个`digit`大小的空间，多出来的这些空间自然是按顺序存储在`PyLongObject`的最后一个数据域，也就是`ob_digit[]`的后面，这样一来，使用`ob_digit[2]`、`ob_digit[100]`就可以访问到后面的空间了。
```
   在编译器眼中，PyLongObject还是只有那么短
   但我们开拓出的额外空间也是可以使用的

   +-------------------+   ---             
   | PyObject_VAR_HEAD |    ^              
   |        ...        |    |  PyLongObject
   +-------------------+    |              
   |    ob_digit[0]    |    v              
   +-------------------+   ---             
   |    ob_digit[1]    |  
   +-------------------+
   |    ob_digit[2]    |  
   +-------------------+
   |    ob_digit[3]    |  
   +-------------------+
   |        ...        |  
   +-------------------+
```

使用这种技巧，对于一个`PyLongObject`，在程序运行之后就可以根据实际情况动态地调整分配给`ob_digit`的大小了。

### python中的整型变量真的可变长吗？
如果你告诉任何一个python使用者“python中的整型变量是可变长的”，那么对方可能会认为你是个水货。毕竟整数类型从来也没见过有什么`append`或者下标访问的方法，更没办法遍历。

实际上在cpython中，整型变量对应的`PyLongObject`结构体之所以被视为`PyVarObject`是因为，cpython可能需要不同的位数来表示不同的整型变量，比如整数`10`只需要1个`digit`位就可以表示，但`182308214818329`可能需要多个`digit`位，而它们都是用同一个`PyLongObject`来表示的，所以对于cpython来说，它不能确定整型变量一定会占据几位`digit`；而一旦整数`10`对应的`PyLongObject`被创建，那么这个`digit`的位数就已经固定下来了，在接下来的运行中将永远不会改变。

所以说整型“可变长”，只是在cpython眼中属于这个类型的不同变量的长度有可能不一样，并不意味着某个属于这个类型的变量的长度“可改变”。

## 参考
- 《python源码剖析》陈儒（注：此书2008年出版，是基于python2编写的，本文基于python3编写）
- python官网文档，[CPython’s internals](https://devguide.python.org/internals/)
- [Your Guide to the CPython Source Code](https://realpython.com/cpython-source-code-guide)
- python3 source code analysis，[Python 整数对象](https://flaggo.github.io/python3-source-code-analysis/objects/long-object/)
- 博客园，来自东方地灵殿的小提琴手，[《深度剖析CPython解释器》2. 解密PyObject、PyVarObject、PyTypeObject在Python对象体系中所代表的含义，用CPython来总结Python中type和object之间的关系](https://www.cnblogs.com/traditional/p/13398797.html)
- w3cschool，猿友，[python源码剖析之PyObject详解](https://www.w3cschool.cn/article/29330845.html)
- 白日梦想猿，[《Python源码剖析》之对象的基石---PyObject](http://www.lll.plus/zh/blog/content?id=1428)