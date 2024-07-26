[《PC Assembly Language》](http://pacman128.github.io/static/pcasm-book.pdf)[Paul A. Carter](http://pacman128.github.io/)
## 第7章-结构体与C++（Structures and C++）
### 7.1 结构体
ANSI C标准规定：
1. 结构体中各变量的排序与在内存中的排序相同；
2. 第一个变量相对结构体地址的偏移量为0；
3. 在`stddef.h`中定义了宏`offsetof()`，可以用来计算结构体中变量相对结构体地址的偏移量（用法为`offsetof(strut, var)`，strut为结果体名，var为结构体中的变量名）。

#### 7.1.2 内存对齐（Memory alignment）
结构体中的变量通常以4B对齐。
> 在汇编中，对不对齐可以自己决定，但若要与C交互，就得统一标准。

```
struct S {
        short int x; /∗ 2−byte integer ∗/
        int y; /∗ 4−byte integer ∗/
        double z; /∗ 8−byte float ∗/
};
       0       2B       4B
0x00   +--------+--------+
       |   x    |(unused)|
0x04   +--------+--------+
       |        y        |
0x08   +-----------------+
       |                 |
0x0C   +        z        +
       |                 |
0x10   +-----------------+
```

> 但其实ANSI C标准并没有规定对齐方式，所有不同编译器对结构体的内存处理各有千秋。
如Borland编译器就不会像上面那样对齐，而是直接按顺序存放。

gcc编译器提供了一个灵活的方式来可以来调整对齐：
```c
typedef short int unaligned int __attribute__ (( aligned (1)));
```
将short int类型定义为unaligned，后面的1表示以1B对齐，也可以改成任何等于2的n次幂的数字，2表示2B对齐，4表示4B对齐。

gcc还提供了`pack`操作：
```c
#pragma pack(1)  // 这告诉编译器让结构体尽可能占用最少的字节。
#pragma pack(2)  // 这告诉编译器让结构体尽可能占用最少的字。
#pragma pack(4)  // 这告诉编译器让结构体尽可能占用最少的双字。
```
pack会一直生效直到遇见下一个pack。

所以若一个C文件中引入了带有pack的头文件，那么这个C文件中的结构体的对齐方式也会受到影响。

为解决此问题，微软和Borland是这么做的：
```c
#pragma pack(push)  // save alignment state
#pragma pack(1)  // set byte alignment 
struct S {
    short int x; // 2−byte integer
    int y; // 4−byte integer 
    double z; // 8−byte float 
};
#pragma pack(pop)  // restore original alignment
```

#### 7.1.3 位域（Bit Fields）
使用`unsigned int`或`int`加上冒号再加上位数来指定一个变量所拥有的比特位。
```c
struct S {
    unsigned f1 : 3;  // 3−bit field
    unsigned f2 : 10; // 10−bit field
    unsigned f3 : 11; // 11−bit field
    unsigned f4 : 8; // 8−bit field
};
```

上面这个结构体在内存中的样子应该是：
```

||8bit       0||8bit       0||8bit       0||8bit       0||
++-------+----++------+-----++------------++------------++
|| f2l   | f1 || f3l  | f2m ||    f3m     ||     f4     ||
++-------+----++------+-----++------------++------------++

   第1个字节      第2个字节      第3个字节      第4个字节 
```

