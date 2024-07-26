[《PC Assembly Language》](http://pacman128.github.io/static/pcasm-book.pdf)[Paul A. Carter](http://pacman128.github.io/)
## 第4章-子程序Subprograms
### 4.1 间接寻址（Indirect Addressing）
```assembly
mov ax, [Data] ; normal direct memory addressing of a word
mov ebx, Data ; ebx = & Data
mov ax, [ebx] ; ax = *ebx
```
> 因为ax大小为1个字，所以会从以ebx为起始的地址开始读取一个字，并存入ax中。
若用al代替ax，因为al大小为1个字节，所以会从以ebx为起始的地址开始读取一个字节，并存入al。
所以从ebx指向的地址开始读入多长的数据完全由寄存器的大小决定。
若错误地使用寄存器，汇编器并不会报错，但程序却会错误。

所有32-bit通用寄存器和索引寄存器都可以用于简介寻址，但通常16-bit和8-bit寄存器不可以。

### 4.2 简单的子程序实例

### 4.3 栈（The Stack）
SS端寄存器指明了存放栈的段（通常就是存放数据的段，即data segment）。
ESP寄存器存放了栈中最顶部数据的地址（sp是stack pointer的缩写）。
入栈的数据单位只能是2个字（即不可一次入栈1B）（事实上也可以压入1个字，但在32-bit保护模式下，最好还是用2个字）。

`push`指令将一个2个字的数据压入栈：先将esp的值减4，然后存放2个字的数据进\[esp\]。
`pop`指令从\[esp\]读入2个字数据，然后给esp的值加4。

`pusha`指令可以将`EAX`、`EBX`、`ECX`、`EDX`、`ESI`、`EDI`和`EBP`一次性入栈（但不是按照这个顺序）；
`popa`指令可以将上面入栈的数据都弹回寄存器。

### 4.4 CALL与RET指令（The CALL and RET Instructions）
`call`指令无条件跳转到子程序，且将下一条指令的地址压入栈；
`ret`指令将压入的地址弹出，并跳转到这个地址指向的指令。

### 4.5 调用约定（Calling Conventions）
> 调用函数时，调用程序和被调用程序要在如何传递参数这个问题上达成一致，这叫Calling Conventions。

#### 4.5.1 用栈传递参数（Passing parameters on the stack）
通过栈把参数传递给子程序，需要将`call`指令之前将参数压入栈中。
与C一样，若想要在子程序中改变参数的值，需要传递参数的地址，而不是参数值。

若参数值的长度小于2个字，则需要先转化为2个字长度的数据，再压入栈中。

压入栈中的参数并不是通过出栈来使用的，而是通过栈顶指针+偏移量来访问的。
因为：
- 执行`call`时，先将实参入栈，再将调用程序的指令地址入栈，所以如果要通过出栈访问函数实参，调用函数的指令地址就会丢失。
- `push`会将栈中数据弹出到寄存器中，但在子程序中这些参数不可能一直留在寄存器中，而应该保存在内存中，以便需要的时候再访问。

> 经过考证，在64位机器上，`call`指令的效果仅包含将调用函数处的下一条指令压入栈（此时sp的指也会变化）和跳转到被调用函数。

> 一个单参数函数被调用时，栈的形态如下：
```
        |                |
        |----------------|
ESP + 4 |    Parameter   |
        |----------------|
ESP     | Return address |
        |----------------|
        |                |
```
此时参数可以用`[ESP+4]`来寻址得到。
但若子程序中也需要往栈中压入数据，那么栈的形态就会变成
```
        |                |
        |----------------|
ESP + 8 |    Parameter   |
        |----------------|
ESP + 4 | Return address |
        |----------------|
ESP     |subprogram data |
        |----------------|
```
此时参数的访问地址不再是`[ESP+4]`了。
如何解决呢？

80386提供了EBP寄存器（BP，Base Pointer），这个寄存器的唯一作用是保存指向栈顶的指针。

C调用约定为，子程序执行的头一条语句需要先把EBP的值压入栈中
```
[子程序开始]
        |                |
        |----------------|         ----------------
ESP + 4 |    Parameter   |    EBP | ori_val_in_EBP |
        |----------------|         ----------------
ESP     | Return address |
        |----------------|
        |                |
        |----------------|

[执行] push ebp （将EBP中的值压入栈中）

        |                |
        |----------------|         ----------------
ESP + 8 |    Parameter   |    EBP | ori_val_in_EBP |
        |----------------|         ----------------
ESP + 4 | Return address |
        |----------------|
ESP     | ori_val_in_EBP |
        |----------------|

[执行] move ebp, esp （这样一来，esp就可以随意更改，而仍可以通过ebp来找到参数的地址。）

        |                |
        |----------------|         ----------------
ESP + 8 |    Parameter   |    EBP |    0xABCDE     |
        |----------------|         ----------------
ESP + 4 | Return address |
        |----------------|
ESP=EBP | ori_val_in_EBP | <-- 0xABCDE（假设栈顶位于此地址）
        |----------------|


[执行子程序代码……]

[执行] pop ebp （将原本位于ebp中的值弹回ebp中）

        |                |
        |----------------|         ----------------
ESP + 4 |    Parameter   |    EBP | ori_val_in_EBP |
        |----------------|         ----------------
ESP     | Return address |
        |----------------|
        |                |
        |----------------|

[执行] ret （返回调用函数）
```

子程序结束之后，压入栈中的参数必须被移除。
C调用约定中，由父程序负责做这件事；
但也有别的语言是让子程序做这件事，例如Pascal——有另一种形式的`ret`指令可以方便地实现这一功能。
一些C编译器也支持这一功能，可以在C函数原型和定义中使用`pascal`来告诉编译器要使用Pascal的约定。
MS Windows API C函数使用的stdcall约定也是这么工作的。

那么这种约定的优势是啥？
——它会更有效一些。

那为什么所有C函数都不适用Pascal约定呢？
——通常C语言允许函数拥有可变的参数个数，这样一来，由于这些函数的参数数量是可变的，编译器无法事先知道有多少个参数传递给函数。因此，在每次调用这些函数时，编译器需要参数数量和类型来正确地从堆栈中移除参数。
而C约定能方便地正确移除参数，而对于Pascal和stdcall约定则会非常困难。
所以Pascal并不支持可变参数函数；而对于MS Windows，它的API都是定长参数的，不存在此问题。

例：
```assembly
push dword 1 ; pass 1 as parameter
call fun
add esp, 4 ; remove parameter from stack
```
> 用`pop`来移除参数也可以；
`add`的优点是不需使用寄存器，缺点是`add`指令比`pop`多一个字节。

#### 4.5.2 栈中的局部变量（Local variables on the stack）
静态变量和全局变量在程序执行期间将一直占用内存空间；
而栈中局部变量只有在子程序运行期间才会存在；
因此栈中局部变量可以节省内存。

栈中局部变量从EBP所指地址开始存储。

例，子程序中局部变量的分配：
```assembly
subprogram_label:
push ebp ; save original EBP value on stack
mov ebp, esp ; new EBP = ESP
sub esp, LOCAL_BYTES ; = # bytes needed by locals
; subprogram code
mov esp, ebp ; deallocate locals
pop ebp ; restore original EBP value
ret
```
EBP寄存器用于访问局部变量。

栈帧（stack frame）= 函数参数+返回信息+局部变量

一个子程序的开头（prologue）与结尾（epilogue）可以分别用`enter`和`leave`指令来简单地完成。
> 但一般很少用，因为速度较慢。

`enter`有两个立即数参数，第一个参数是局部变量所需的字节数，第二个参数在C调用约定下永远是0。
```assembly
subprogram_label:
enter LOCAL_BYTES, 0 ; = # bytes needed by locals
; subprogram code
leave
ret
```

### 4.6 多模块程序（Multi-Module Programs）
一个模块中的变量通过`global`变量来导出；通过`extern`来导入别的模块的`global`变量。
```assembly
; 数据标签也可以通过同样形式导入导出
segment .text
    global _asm_main  ; 
    extern get_int, print_sum  ; 导入代码标签
```

### 4.7 与C交互（Interfacing Assembly with C）
两种方式：
1. C内联汇编：方便，但只能使用编译器支持的汇编语法（没有编译器支持NASM语法）。
2. C调用汇编：（1）直接数据访问依赖于硬件特性，而在C中难以实现时；（2）当程序员可以用汇编把程序性能优化到强于编译器时（现代编译器已经拥有很强的优化能力了，此原因已经不再显著）。但这种方式的可读性和可移植性较差）。

> 不同编译器支持不同的汇编语法。
Borland和微软支持MASM格式；DJGPP和Linux gcc需要GAS——一种所有GNU编译器都支持的格式，使用AT&T语法。

#### 4.7.1 Saving registers
C语言默认假设子例程不会改变EBX、ESI、EDI、EBP、CS、DS、SS、ES的值。
这并不意味着子例程不能改变这些寄存器的值，而是表示若更改了这些寄存器的值，则在子程序返回之前，必须原来存放于这些寄存器中的值存回去。
EBX、ESI和EDI不允许更改，因为C语言把它们用于存放寄存器变量。
通常栈用于保存这些寄存器原来的值。

#### 4.7.2 Labels of functions
函数名、全局/静态变量的名字在被许多编译器编译之后都会加上下划线前缀。
> 例如函数f，编译之后就是_f。

Linux gcc编译器是个例外（Linux ELF可执行文件）

#### 4.7.3 Passing parameters
在C调用约定中，函数中位于后面的参数会先被压入栈中。
例如`printf("x = %d", x);`，x会先被压入栈，然后才是字符串`"x=%d"`（format字符串）的地址。

```
EBP + 12|      value of x        |
        |------------------------|
EBP + 8 |address of format string|
        |------------------------|
EBP + 4 |     Return address     |
        |------------------------|
EBP     |     ori_val_in_EBP     |
        |------------------------|
```

因为format字符串是总最后入栈的，它在栈中的位置总可以通过EBP+8来访问（无论传入了多少参数）。printf中的代码可以通过查看format字符串来判定传入了几个参数。
> 若写出了诸如`printf("x = %d\n")`之类的错误代码，printf仍然会将\[EBP+12\]处的双字值打印出来。

#### 4.7.4 Calculating addresses of local variables
找到定义在data或bss段中的标签的地址非常容易（通常链接器完成这个任务）。
但计算栈中局部变量的地址并不那么简单。

假设变量x位于栈中EBP-8的位置，
`mov eax, ebp-8`将是错误的计算方法，因为在这条指令中，mov接收的第二个参数不能是一个表达式。

`lea eax, [ebp - 8]`是专门用于解决这种问题的。
> 看起来`lea`指令在访问内存，但实际上`lea`永远不会访问内存，它只是计算出ebp-8处的值的地址，然后将地址传入eax中。
因为不涉及访存，所以不需要用诸如`dword`的关键字来指明访问的数据的长度。

#### 4.7.5 Returning values
C调用约定通过寄存器传递返回值。
所有整型变量（char、int、enum、etc.）通过EAX寄存器返回。
指针也通过EAX返回。
> 短于32-bit的数据将会被扩展为32-bit，再放入EAX中。

64-bit的数据将放入EDX:EAX寄存器对中。

浮点数将放入数学协处理器的ST0寄存器中。

#### 4.7.6 Other calling conventions
gcc编译器可以显式地指定C函数调用的约定：
```c
void f ( int ) __attribute__ ((cdecl)); // 显式使用cdecl调用约定
void f ( int ) __attribute__ ((stdcall)); // 显式使用stdcall调用约定
// stdcall和cdecl的区别在于stdcall需要子程序去移除栈中的函数参数
// stdcall只能用于固定参数数量的函数
```
> cdecl约定称为标准调用约定（the standard calling
convention），而stdcall称为标准call调用约定（the standard call calling
convention

而Borland和微软使用以下语法显示地指定调用约定
```c
void cdecl f ( int );
```

gcc还支持`regparm`约定，这种约定通过寄存器传递参数。


cdecl：
- 优点：简单灵活；可应用于多种C函数和C编译器；
- 缺点：慢；使用的内存较多。（因为每次调用都需要代码来移除栈中的参数）

stdcall：
- 优点：使用内存较少；在`call`指令之后不需要清理堆栈。
- 缺点：不可用于可变参数数量函数。

regparm：
- 优点：速度快；
- 缺点：复杂；当参数多了之后，有些参数在寄存器中，有些在栈中。

#### 4.7.8 Calling C functions from assembly

### 4.8 可重入和递归子程序
可重入子程序需要满足：
- 不改变任何指令（这在高级语言中很难实现，但汇编可以）；
- 不改变全局变量，且子程序的所有变量都存储在栈中；

可重入子程序优点：
- 可以递归地调用；
- 可以被多个进程共享（ddl文件和共享库就使用了这一思想）；
- 在多线程程序中性能更优；

#### 4.8.1 递归子程序（Recursive subprograms）
直接递归：foo调用foo；
间接递归：foo调用bar，bar再调用foo。

递归子程序必须有终止条件：即当条件满足时，不再递归调用。

#### 4.8.2 回顾C存储类型（Review of C variable storage types）
**global**：
定义于任何函数外面，且存于固定的内存空间（在data和bss段中），在程序执行时一直存在。
默认情况下可以被程序中任何函数访问。
若用static标识，则只能被当前模块访问（在汇编语言中用internal标识）

**static**：
在某一函数中用static标识声明的**局部变量**（很不幸，C语言的static有两种意义），这种变量存储在固定的内存空间（data或bss），但只能被定义它的函数访问。

**automatic**：
就是默认的局部变量，存于函数栈中。

**register**：
此关键字仅仅是一个要求，编译器不一定要遵循。
若要使用变量的地址，则编译器不会将该变量存于寄存器（因为寄存器没有地址）；只有简单的整型数据可以是寄存器变量，结构体不行（放不下）。
C编译器通常会在程序员不知情的情况下把合适的变量定义为寄存器类型。

**volatile**：
此关键字告诉编译器此变量需要经常修改。
通常编译器会将一个变量的值暂时存在寄存器中，而且在出现这个变量的代码部分使用这个寄存器。但是，编译器不能对不稳定类型的变量做这种类型的
优化。
一个不稳定变量的最普遍的例子就是：它可以被多线程程序的两个线程修改。
例如：
```c
x = 10;
y = 20;
z = x;
```
如果x可以被另一个线程修改。那么其它线程可以会在第1行和第3行之间修改x的值，以致于z将不会等于10.但是，如果x没有被声明为不稳定类型，编译器就会推断x没有改变，然后再将z置为10。
不稳定类型的另一个作用就是避免编译器将变量用作寄存器变量。

