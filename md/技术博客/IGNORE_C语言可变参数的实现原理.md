# C语言可变参数函数的实现原理
首次编辑：24/5/18/21:53
最后编辑：24/5/19/

## 参考链接
1. [揭密X86架构C可变参数函数实现原理-CSDN博客](https://blog.csdn.net/linyt/article/details/79772742)
2. [【C语言】可变参数原理与printf的实现](https://blog.csdn.net/weixin_42258222/article/details/118358133)

## 0 说明
本来是搜了一下printf这个可变参数函数的实现原理，后来看着看着看到`<stdarg.h>`头中使用`va_start`、`va_arg`和`va_end`实现可变参数函数的实现原理，就根据找到的资料自己实验了一下。
用了两个系统实验了一下，分别使用不同的编译器。
1. windows
        - 编译器：mingw
        - 架构：x86-64

2. Ubuntu
        - 编译器：GNU gcc
        - 架构：x86-64

结果不尽相同，甚至可以说区别很大。但从实验结果看，个人怀疑mingw应该是根据案例的特殊性进行了优化，不过应该也都值得学习一下。

我使用了下面代码作为例子进行分析：
```c
#include <stdarg.h>
#include <stdio.h>

long sum(long num, ...)
{
        va_list ap;
        long sum = 0;

        va_start(ap, num);

        while(num--) {
                sum += va_arg(ap, long);
        }

        va_end(ap);
        return sum;
}

int main()
{
        long ret;
        ret = sum(8L, 1L, 2L, 3L, 4L, 5L, 6L, 7L, 8L);
        printf("sum(1..8) = %ld\n", ret);

        return 0;
}
```
其中参数都为long类型，占8字节。

## 1 前置知识
### 1.1 调用约定、汇编
早期架构中，C语言中函数的实参是通过函数栈传递的。然而在x86架构中，实参不再完全通过函数栈传递，前若干个实参（具体多少因编译器不同而不同）通过寄存器传递，旨在减小开销提高效率。
传递参数的方式被称为**调用约定（calling convention）**，不同编译器的调用约定不尽相同。
通过实验，x86-64Windows下的mingw编译器的前4个实参通过寄存器传递：
1. ecx
2. edx
3. r8d
4. r9d

而x86-64Ubuntu下的GNU gcc编译器的前6个实参通过寄存器传递：
1. rdi
2. rsi
3. rdx
4. rcx
5. r8d
6. r9d

而如果实参数量大于这些寄存器的数量，则使用函数栈传递其余的参数。

--- 

除此之外应该对汇编语言有一些基本的了解。

### 1.2 关于va_start和va_arg的使用
va_start的作用是告知哪个参数之后才是可变参数，以sum函数为例：
```c
va_start(ap, num);
```
这句话告诉我们，num参数之后的，就是可变参数了，即ap描述的参数列表从是从第二个参数开始的。

在此之后，每执行一次va_arg就能获取一个可变参数，va_arg的第二个参数指明了参数的类型。
```c
va_arg(ap, long);  // 从可变参数列表获取下一个参数，其类型为long
```

## 2 阅读汇编码之后得出的结论
### 2.1 windows-mingw
可能因为本例中的可变参数都为long类型，比较易于处理，编译时我也没开什么编译器选项，所以mingw编译器采取的可变参数函数实现策略好像和va_list没什么关系了——直接使用了函数栈传参的方式。
在调用sum函数的时候，main函数会首先从右到左将参数压入函数栈（除了前四个参数，它们会通过寄存器传递）。
如下图所示，栈底在上，栈顶在下，所以最后一个实参在最上方，也就是8。
```
+-------------+--------------+
|    Value    |   Address    |
+-------------+--------------+
|             |    0x1000    | <-- rbp_main
+-------------+--------------+
|    ....     |     ....     |
+-------------+--------------+
|     8       |    0x0fe0    |
+-------------+--------------+
|     7       |    0x0fd8    |
+-------------+--------------+
|     6       |    0x0fd0    |
+-------------+--------------+
|     5       |    0x0fc8    |
+-------------+--------------+
|     4       |    0x0fc0    |
+-------------+--------------+
|             |    0x0fb8    |
+-------------+--------------+
|             |    0x0fb0    |
+-------------+--------------+
|             |    0x0fa8    |
+-------------+--------------+
|             |    0x0fa0    | <-- rsp_main
+-------------+--------------+
```
这里为了演示方便，我用rbp_main和rsp_main分别标注了main函数的栈底和栈顶（实际上rbp和rsp这两个寄存器专门用于标明当前函数栈的栈底和栈顶，但由于调用sum之后，这两个寄存器的值会发生改变，所以我用_main来标注这是属于main的栈底和栈顶）。
我们可以发现，sum函数的实参压入之后，仍然有4个4B（一个long类型的长度）空间没有使用，这是干什么的呢？
另外的4个实参8L、1L、2L、3L分别存放在ecx、edx、r8d、r9d中。

接着在汇编码中，main函数调用`call sum`指令，调用sum函数。此时执行完sum函数之后的返回地址会被压入栈中，接着main函数的栈底被压入栈中。这两部是为了能够在执行完sum之后返回到main函数中。
然后寄存器rbp和rsp会分别更新为sum函数的函数栈底和栈顶，如下图所示：
```
+-------------+--------------+
|    Value    |   Address    |
+-------------+--------------+
|             |    0x1000    | <-- rbp_main
+-------------+--------------+
|    ....     |     ....     |
+-------------+--------------+
|     8       |    0x0fe0    |
+-------------+--------------+
|     7       |    0x0fd8    |
+-------------+--------------+
|     6       |    0x0fd0    |
+-------------+--------------+
|     5       |    0x0fc8    |
+-------------+--------------+
|     4       |    0x0fc0    |
+-------------+--------------+
|             |    0x0fb8    |
+-------------+--------------+
|             |    0x0fb0    |
+-------------+--------------+
|             |    0x0fa8    |
+-------------+--------------+
|             |    0x0fa0    | <-- rsp_main
+-------------+--------------+
| ret_address |    0x0f98    |
+-------------+--------------+
|   0x1000    |    0x0f90    | <-- rbp_sum
+-------------+--------------+
|             |    0x0f88    |
+-------------+--------------+
|             |    0x0f80    | <-- rsp_sum
+-------------+--------------+
```
接着接着就是关键的地方了，这个时候它居然把前4个实参放在了刚刚main函数栈顶的4个4B空间处：
```
+-------------+--------------+
|    Value    |   Address    |
+-------------+--------------+
|             |    0x1000    | <-- rbp_main
+-------------+--------------+
|    ....     |     ....     |
+-------------+--------------+
|     8       |    0x0fe0    |
+-------------+--------------+
|     7       |    0x0fd8    |
+-------------+--------------+
|     6       |    0x0fd0    |
+-------------+--------------+
|     5       |    0x0fc8    |
+-------------+--------------+
|     4       |    0x0fc0    |
+-------------+--------------+
|     3       |    0x0fb8    |
+-------------+--------------+
|     2       |    0x0fb0    |
+-------------+--------------+
|     1       |    0x0fa8    |
+-------------+--------------+
|  num = 8    |    0x0fa0    | <-- rsp_main
+-------------+--------------+
| ret_address |    0x0f98    |
+-------------+--------------+
|   0x1000    |    0x0f90    | <-- rbp_sum
+-------------+--------------+
|             |    0x0f88    |
+-------------+--------------+
|             |    0x0f80    | <-- rsp_sum
+-------------+--------------+
```
也就是说编译器通过num这个参数的实参8，知道了会有8个可变参数，所以1+8总共9个实参，于是把后5个实参通过函数栈传递，然后前4个实参通过寄存器传递，再放入了函数栈中！所以其实本质上是所有的实参都通过函数栈进行传递，而第一个实参8让编译器知道了会有几个可变参数，于是编译器在main的函数栈中为这9个实参都留好了位置。使用寄存器这个中间商简直是脱裤子放屁——多此一举！

于是sum函数只需要知道第一个实参的地址，然后通过4B的偏移量来访问下一个实参。

然而这种情况相当特殊，因为所有实参都是4B的long类型，所以通过函数栈这种原始的方式传递可变参数相当方便，以至于程序中根本没有用到va_list这个结构。当然这应该是编译器优化之后的结果。

不过在Ubuntu下，GNU gcc编译出来的结果可就不同了——它真真切切地使用到了va_list。

#### 汇编码
最后给出在Windows下使用mingw编译之后的汇编码：
```assembly
<sum>        push   %rbp
<sum+1>      mov    %rsp,%rbp
<sum+4>      sub    $0x10,%rsp
<sum+8>      mov    %ecx,0x10(%rbp)     ; 将第一个参数num放在main函数栈中
<sum+11>     mov    %rdx,0x18(%rbp)     ; 将第二个……
<sum+15>     mov    %r8,0x20(%rbp)      ; 将第3个……
<sum+19>     mov    %r9,0x28(%rbp)      ; 将第4个……
<sum+23>     movl   $0x0,-0x4(%rbp)     ; 初始化sum
<sum+30>     lea    0x18(%rbp),%rax     ; 把第二个参数的地址放到rax中
<sum+34>     mov    %rax,-0x10(%rbp)    ; 把rax的值（第二个参数的地址）放到sum函数栈中
<sum+38>     jmp     <sum+57>
<sum+40>     mov    -0x10(%rbp),%rax    ; 把-0x10(%rbp)（位于sum函数栈，此前存储上一个参数的地址）的值，放到eax中
<sum+44>     lea    0x8(%rax),%rdx      ; 把eax的值加8，然后放入rdx（实现va_arg(ap, long)，即获取下一个参数的地址）
<sum+48>     mov    %rdx,-0x10(%rbp)    ; 把下一个参数的地址放入-0x10(%rbp)（位于sum函数栈，此前存储上一个参数的地址）
<sum+52>     mov    (%rax),%eax         ; 将rax中的地址指向的内存单位的值放入eax中（即获取参数的值）
<sum+54>     add    %eax,-0x4(%rbp)     ; 将eax与-0x4(%rbp)（即sum）相加（即将参数的值与sum相加）
<sum+57>     mov    0x10(%rbp),%eax     ; 将num放到eax中
<sum+60>     lea    -0x1(%rax),%edx     ; num - 1，然后放入edx中
<sum+63>     mov    %edx,0x10(%rbp)     ; 将edx的值放回存储第一个参数（即num）的地址处
<sum+66>     test   %eax,%eax           ; 测试eax是否为0
<sum+68>     jne     <sum+40>           ; 若不为0，跳转
<sum+70>     mov    -0x4(%rbp),%eax
<sum+73>     add    $0x10,%rsp
<sum+77>     pop    %rbp
<sum+78>     ret 
<main>       push   %rbp
<main+1>     mov    %rsp,%rbp
<main+4>     sub    $0x60,%rsp
<main+8>     call   <__main>
<main+13>    movl   $0x8,0x40(%rsp)     ; 从这里开始是后5个实参入栈的过程
<main+21>    movl   $0x7,0x38(%rsp)
<main+29>    movl   $0x6,0x30(%rsp)
<main+37>    movl   $0x5,0x28(%rsp)
<main+45>    movl   $0x4,0x20(%rsp)
<main+53>    mov    $0x3,%r9d           ; 从这里开始是前4个实参入寄存器的过程
<main+59>    mov    $0x2,%r8d
<main+65>    mov    $0x1,%edx
<main+70>    mov    $0x8,%ecx
<main+75>    call   <sum>
<main+80>    mov    %eax,-0x4(%rbp)
<main+83>    mov    -0x4(%rbp),%eax
<main+86>    mov    %eax,%edx
<main+88>    lea    0x2b02(%rip),%rax
<main+95>    mov    %rax,%rcx
<main+98>    call   <printf>
<main+103>   mov    $0x0,%eax
<main+108>   add    $0x60,%rsp
<main+112>   pop    %rbp
<main+113>   ret
```

### 2.2 Ubuntu-GNU gcc


```assembly

<sum>            endbr64
<sum+4>          push      %rbp
<sum+5>          mov       %rsp,%rbp
<sum+8>          sub       $0xf0,%rsp
<sum+15>         mov       %rdi,-0xe8(%rbp)     ; 第1个参数
<sum+22>         mov       %rsi,-0xa8(%rbp)     ; 第2个参数
<sum+29>         mov       %rdx,-0xa0(%rbp)     ; 第3个参数
<sum+36>         mov       %rcx,-0x98(%rbp)     ; 第4个参数
<sum+43>         mov       %r8,-0x90(%rbp)      ; 第5个参数
<sum+50>         mov       %r9,-0x88(%rbp)      ; 第6个参数
<sum+57>         test      %al,%al              ; 在main中已经把eax设置为0了，此时判断al必然成立，故je一定可以跳转
<sum+59>         je        <sum+93>
<sum+61>         movaps    %xmm0,-0x80(%rbp)
<sum+65>         movaps    %xmm1,-0x70(%rbp)
<sum+69>         movaps    %xmm2,-0x60(%rbp)
<sum+73>         movaps    %xmm3,-0x50(%rbp)
<sum+77>         movaps    %xmm4,-0x40(%rbp)
<sum+81>         movaps    %xmm5,-0x30(%rbp)
<sum+85>         movaps    %xmm6,-0x20(%rbp)
<sum+89>         movaps    %xmm7,-0x10(%rbp)
<sum+93>         mov       %fs:0x28,%rax        ; 实现栈保护的
<sum+102>        mov       %rax,-0xb8(%rbp)     ; 应该也是栈保护的
<sum+109>        xor       %eax,%eax            ; 意思是将eax清零，这条语句操作码小于mov，节省内存
<sum+111>        movq      $0x0,-0xd8(%rbp)     ; 初始化sum为0，sum存储在-0xd8(%rbp)处
<sum+122>        movl      $0x8,-0xd0(%rbp)     ; 这个应该是gp_offset
<sum+132>        movl      $0x30,-0xcc(%rbp)    ; 这个应该是fp_offset
<sum+142>        lea       0x10(%rbp),%rax      ; 将第7个参数的地址放在-0xc8(%rbp)处（即overflow_reg_area）
<sum+146>        mov       %rax,-0xc8(%rbp)  
<sum+153>        lea       -0xb0(%rbp),%rax     ; -0xc0(%rbp)处放的应该是reg_save_area
<sum+160>        mov       %rax,-0xc0(%rbp)
<sum+167>        jmp       <sum+243>

<sum+169>        mov       -0xd0(%rbp),%eax     ; 
<sum+175>        cmp       $0x2f,%eax           ; 若47 > eax则跳转，否则不跳转。为啥是47呢，因为有6个long类型参数通过寄存器传递，long占8B，6*8 = 48。ja是大于时跳转，所以用48-1=47
<sum+178>        ja        <sum+215>
<sum+180>        mov       -0xc0(%rbp),%rax     ; 将-0xc0(%rbp)（即reg_save_area）的值放入rax中
<sum+187>        mov       -0xd0(%rbp),%edx     ; 将gp_offset放入edx中
<sum+193>        mov       %edx,%edx            ; 空操作
<sum+195>        add       %rdx,%rax            ; 效果为reg_save_area += gp_offset
<sum+198>        mov       -0xd0(%rbp),%edx     ; （和下面三行）效果为gp_offset += 8
<sum+204>        add       $0x8,%edx
<sum+207>        mov       %edx,-0xd0(%rbp)
<sum+213>        jmp       <sum+233>

<sum+215>        mov       -0xc8(%rbp),%rax     ; 将第当前参数的地址传给rax
<sum+222>        lea       0x8(%rax),%rdx       ; 将该地址+8之后（即获得下一个参数的地址），放入rdx
<sum+226>        mov       %rdx,-0xc8(%rbp)     ; 将下一个参数的地址放入-0xc8(%rbp)（即overflow_reg_area）

<sum+233>        mov       (%rax),%rax          ; 取得当前参数的值，放入rax
<sum+236>        add       %rax,-0xd8(%rbp)     ; 将当前参数的值与sum相加，结果存储在sum中

<sum+243>        mov       -0xe8(%rbp),%rax     ; 将num放入rax
<sum+250>        lea       -0x1(%rax),%rdx      ; 将rax减掉1，放入rdx（即num--）
<sum+254>        mov       %rdx,-0xe8(%rbp)     ; 将num放回其存储位置
<sum+261>        test      %rax,%rax            ; 测试num是否为0，是则不跳转
<sum+264>        jne       <sum+169>
<sum+266>        mov       -0xd8(%rbp),%rax     ; 将sum存入rax，作为返回值
<sum+273>        mov       -0xb8(%rbp),%rcx     ; 下面是栈保护的
<sum+280>        xor       %fs:0x28,%rcx
<sum+289>        je        <sum+296>
<sum+291>        callq     <__stack_chk_fail@plt>
<sum+296>        leaveq
<sum+297>        retq   
<main>           endbr64
<main+4>         push      %rbp
<main+5>         mov       %rsp,%rbp
<main+8>         sub       $0x10,%rsp
<main+12>        sub       $0x8,%rsp
<main+16>        pushq     $0x8
<main+18>        pushq     $0x7
<main+20>        pushq     $0x6
<main+22>        mov       $0x5,%r9d
<main+28>        mov       $0x4,%r8d
<main+34>        mov       $0x3,%ecx
<main+39>        mov       $0x2,%edx
<main+44>        mov       $0x1,%esi
<main+49>        mov       $0x8,%edi
<main+54>        mov       $0x0,%eax  
<main+59>        callq     <sum>
<main+64>        add       $0x20,%rsp
<main+68>        mov       %rax,-0x8(%rbp)
<main+72>        mov       -0x8(%rbp),%rax
<main+76>        mov       %rax,%rsi
<main+79>        lea       0xd1b(%rip),%rdi
<main+86>        mov       $0x0,%eax
<main+91>        callq     <printf@plt>
<main+96>        mov       $0x0,%eax
<main+101>       leaveq
<main+102>       retq   
```