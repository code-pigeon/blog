# gcc笔记——动态库
首次编辑：24/8/17/16:55
最后编辑：24/8/17/17:18

## 位置无关代码

动态库应该被编译为位置无关的代码，在这种情况下，glocal offset table这张表记录着所有动态链接符号的位置。

`-fpic`和`-fPIC`选项都可以生成位置无关的代码。前者编译出更快的代码，但对于global offset table的尺寸有限制，后者则没有。

## 三种名字
- real name：`.so`文件的真实名字，通常遵循`libname.so.x.y.z`的结构，`name`即为动态库的名字，`x`、`y`、`z`分别代表大、小版本号和发布号。
- Shared Object Name（soname）：`libname.so.x`，即只带有大版本号的名字，通常是个指向real name文件的符号链接。
- Linker name：`libname.so`，即不带任何版本号的名字，通常是个指向soname文件的符号链接。

## 动态库的创建
1. 位置无关的目标文件
```bash
gcc -fpic -c source1.c source2.c
```

2. 位置无关的动态库
```bash
gcc -fpic source1.o source2.o -shared -Wl,-soname,libsource.so.1 -o libsource.so.1.1
```
`-Wl`作用是将后面的选项传递给链接器ld。`-soname`表示在目标库中嵌入soname信息，这样当有可知性文件需要调用库source的时候，就会通过这个soname信息来寻找拥有相同soname的动态库。



## 参考
- [YouTube，Creating and Linking Shared Libraries on Linux with gcc](https://www.youtube.com/watch?v=mUbWcxSb4fw&list=PLIz6U0slZNq2TS1zSUjZHgxBjAJL4nb92&index=6)