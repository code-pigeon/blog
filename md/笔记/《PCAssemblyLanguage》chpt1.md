[《PC Assembly Language》](http://pacman128.github.io/static/pcasm-book.pdf)[Paul A. Carter](http://pacman128.github.io/)
## 第1章-介绍Introduction
### 1.2 Computer Organization
#### 1.2.1 内存（Memory）
|单位|大小|
|----|----|
|word|2 bytes|
|double word|4 bytes|
|quad word|8 bytes|
|paragraph|16 bytes|

#### 1.2.3 80x86 CPU家族
##### 实模式
- 程序可以访问任何内存地址（甚至是别的程序的内存）
- 程序内存需要分段，每个段不超过64K

##### 16-bit保护模式
- 防止程序访问其它程序的内存
- 至多访问16MB内存地址
- 程序内存需要分段，每个段不超过64K

##### 32-bit保护模式
- 防止程序访问其它程序的内存
- 至多访问4GB内存地址
- 程序内存需要分段，每个段不超过4GB

##### 8088，8086
- 早期电脑使用
- 提供16-bit寄存器AX、BX、CX、DX、SI、DI、BP、SP、CS、DS、SS、ES、IP、FLAGS。
- 1MB内存
- 只支持实模式

##### 80286
- 用于AT级别个人电脑（AT class PC）
- 在8088/86基础上添加了一些新指令
- **提供16-bit保护模式**

##### 80386
- 将很多寄存器扩展至32-bit（EAX、EBX、ECX、EDX、ESI、EDI、EBP、ESP、EIP）
- 新增16-bit寄存器FS、GS
- 新增32-bit保护模式

##### 80486/Pentium/Pentium Pro
- 新增少量增加指令运行速度的特性

##### Pentium MMX
- 添加了MMX指令（MultiMedia eXentions）的Pentium，这些指令可以加速常见的图形操作（graphics operations）

##### Pentium II
- 添加了MMX指令的Pentium Pro

#### 1.2.4 8086 16-bit Registers

##### 通用寄存器（general purpose registers）
8086CPU提供了4个16-bit的通用寄存器：AX、BX、CX、DX。
每个寄存器都可以被分为高低两个8-bit寄存器
```
+------+------+ 
|  AH  |  AL  |    [16bit AX寄存器]
+------+------+
  8bit   8bit  
```

##### 索引寄存器（index registers）
还提供了2个16-bit的索引寄存器：SI、DI
通常作指针使用（但也可以作为通用寄存器使用）
不可以被分为高低两个8-bit寄存器。


##### 16-bit寄存器BP、SP
此二寄存器用于指向机器语言栈中的数据。

##### 段寄存器（segment registers）
16-bit寄存器CS、DS、SS、ES是段寄存器，它们标记了不同程序所使用的内存。
CS（Code Segment）、DS（Data Segment）、SS（Stack Segment）、ES（Extra Segment）。
ES作为临时段寄存器使用。

##### 指令指针寄存器（Instruction Pointer register，IP寄存器）
IP寄存器配合CS寄存器一起用于追踪CPU将执行的下一条指令的地址。
通常情况下，当一条指令执行之后，IP会指向内存中存储的下一条指令。

##### FLAGS寄存器（FLAGS register）
存储了上一个指令的结果信息，FLAGS寄存器的每个bit都存储着一个信息。
例如，当上一条指令的结果是0时，FLAGS寄存器的Z比特会被置为1；如果上条指令结果不是0，Z比特会置为0。

#### 1.2.5 80386 32-bit Registers

80386CPU和之后的CPU都扩展了寄存器。
例如，16-bit的AX被扩展为32-bit。
为了兼容，EAX指扩展后的32-bit寄存器，而AX指EAX的低16bits（但EAX的搞16bits无法直接访问）。
```
|<---------- EAX ---------->|
              |<---- AX --->|

+------+------+------+------+ 
|             |  AH  |  AL  |    [32bit EAX寄存器]
+------+------+------+------+
  8bit   8bit   8bit   8bit  
```

段寄存器仍然是16-bit，但多了两个FS和GS（像ES一样是临时段寄存器）。

#### 1.2.6 实模式（Real Mode）
在实模式下，内存大小只能有1MB。
有效的地址范围是00000到FFFFF（16进制）。表示这些地址需要20-bit。很明显一个寄存器（16-bit）不足以表示一个地址。
所以就只能用2个16-bit来表示一个地址。
段基址（selector）16-bits，段基址必须存储在段寄存器中。
段内偏移量（offset）16-bits。
用`[seletor,offset]`来计算物理地址的方法：`16 * selector + offset`
> 在16进制中乘以16非常简单，只需要在最右边加个0就行了。
例如：若`[seletor, offset] = [047C, 0048]`，则对应地址为047C0 + 0048 = 04808

实分段地址（Real segmented addresses）的缺点：

- 一个选择器值（应该就是表示段名）只能包含64K内存（为偏移offset的大小16bit所限制）。若一个程序大于64K，一个单独的CS值不足以让此程序完整地执行，程序不得不分裂成多个小于64K的部分（段）。当程序从一个部分执行到另一个部分时，CS的值就得改变了。同样的问题也会出现在大块数据和DS寄存器上。
- 内存中的每个字节并没有独一无二的分段地址。物理地址04808可以是`[047C,0048]`，`[047D,0038]`，`[047E,0028]`或者`[047C,0058]`。这将导致分段地址的比较十分复杂。

#### 1.2.7 16-bit保护模式（Protected Mode）
在80286的16-bit保护模式下，selector的值的解释与实模式完全不同。
在实模式下，selector的值是物理内存的段号（paragraph number）
在保护模式下，selector的值是描述表（此处应该指段表）的索引。

两种模式下，程序都会被分段。
在实模式下，这些段位于内存中的固定区域，selector的值表示每个段开始的段号。
在保护模式下，段不在物理内存的固定位置（实际上，它们甚至不需要位于内存中）。（实际上保护模式用的就是虚拟内存技术）

在保护模式下，每个段在段表中都被分配了一个入口（entry），这个entry包含一些必要的段的信息：是否在内存中；在内存中的位置；访问权限（例如只读）。
段入口（entry of the segment）的索引即为selector的值，它被存储在段寄存器中。

> 16-bit保护模式最大的缺点：只有16-bit大小的偏移（offset）——这使得一个段最大仍然只能有64K。对于大数组，这种限制是一种灾难。

#### 1.2.8 32-bit保护模式

80386引入了32-bit保护模式，它的优点是：
1. offset扩展到了32-bits。offset最大可以到4billion，所以一个段可以有4GB大。
2. 一个段可以被分为更小的单元——页，一个页有4K大小，现在虚拟内存技术以页为单位来工作。这意味着在某一时刻，一个段可能只有一小部分处于内存中。

#### 1.2.9 中断（Interrupts）
当有事件需要及时响应时，正常的程序流可能需要被中断。计算机硬件提供了中断（interrupts）机制来处理这些事件。
> 例如：当鼠标移动时，鼠标硬件将中断当前程序以处理鼠标移动事件。

当中断发生时，计算机将启动中断处理器（interrupt handler）——一个处理中断的流程。
计算机分配不同的整型值（integer number）给每一种不同的中断。
在物理内存的起始位置，有一个中断向量表（table of interrupt vectors），它包含着中断处理器的段地址。
中断数字（interrupt number，即前文中“分配不同的整型值给不同中断”的那个整型值）实际上就是中断向量表的索引。

外部中断：由CPU外部发起的中断——鼠标、I/O设备发起的中断。
内部中断：CPU内部发起的中断——错误（error）、中断指令（interrupt instruction）。

错误中断（error interrupts）也称陷阱（traps）。
中断指令产生的中断叫软件中断（software interrupts）


### 1.3 汇编语言（Assembly Language）
通常的格式：`mnemonic operand(s)`（助记符 操作数）

汇编器：将汇编语言翻译为机器语言。
汇编器种类：
- Netwide Assembler（NASM）：开源免费。
- Microsoft’s Assembler (MASM)
- Borland’s Assembler (TASM)

> 以上汇编器语法上稍有不同。

#### 1.3.3 指令操作数（Instruction operands）

操作数类型：
- 寄存器：指寄存器中的内容。
- 内存：指内存中的数据，数据的地址可能是直接被硬编码在指令中的，也可能是通过寄存器中的值计算而得的。地址总是相对于段基址的段内偏移量。
- 立即数（immediate）
- 隐式操作数（implied）

#### 1.3.4 基本指令（Basic instructions）
**mov**
将src表示的数据复制到dest
```assembly
mov dest, src
```
但两个操作数不能同时为内存操作数，两个数据必须有相同的长度。
```assembly
mov eax, 3 ; store 3 into EAX register (3 is immediate operand)
mov bx, ax ; store the value of AX into the BX register
```

**add**
```assembly
add eax, 4 ; eax = eax + 4
add al, ah ; al = al + ah
```

**sub**
```assembly
sub bx, 10 ; bx = bx - 10
sub ebx, edi ; ebx = ebx - edi
```

**inc与dec**
```assembly
inc ecx ; ecx++
dec dl ; dl--
```

#### 1.3.5 指示符（Directives）
指示符是汇编语言的产物，不会被翻译为CPU支持的机器语言。
主要包括：
- 定义常量
- 定义存储数据的内存
- 将内存分段（group memory into segments）
- 条件包含源码
- 包含其它文件

NASM代码的预处理器与C语言的相似。但NASM的预处理器指示符以“%”开始，而不是C语言的“#”

##### equ指示符（The equ directive）
equ指示符用于定义符号（symbol），符号即被命名的常量。
格式为：
```assembly
symbol equ value
```
符号不可以被重新定义。

##### %定义指示符（The %define directive）
%指示符用于定义宏（macros），就像C语言的#。
```assembly
%define SIZE 100
  mov eax, SIZE
```
##### 数据指示符（Data directives）
数据指示符用于在数据段中定义内存空间。（就像在C语言中声明一个变量，其实就是为变量在内存中开辟了一个空间）
有两种方式：
1. 为变量定义内存空间；
2. 为变量定义内存空间同时初始化。

第1种方式使用“RESX”指示符，其中“X”要根据数据长度进行变化，如下表所示：

|Unit|Letter|
|----|------|
|byte|B|
|word|W|
|double word|D|
|quad word|Q|
|ten bytes|T|

> 比如，声明一个字长度的变量就是`L1 resw 1`，L1是这个内存空间的标签（Label）。

第2种方式使用“DX”指示符，“X”一样要根据数据长度进行变化
```assembly
L1 db 0 ; byte labeled L1 with initial value 0
L2 dw 1000 ; word labeled L2 with initial value 1000
L3 db 110101b ; byte initialized to binary 110101 (53 in decimal)
L4 db 12h ; byte initialized to hex 12 (18 in decimal)
L5 db 17o ; byte initialized to octal 17 (15 in decimal)
L6 dd 1A92h ; double word initialized to hex 1A92
L7 resb 1 ; 1 uninitialized byte
L8 db "A" ; byte initialized to ASCII code for A (65)
```

> 单引号和双引号的效果相同。

被定义的数据会按照定义顺序在内存当中连续地存储。

也可以用一个指令连续地开辟空间
```assembly
L9 db 0, 1, 2, 3 ; defines 4 bytes
L10 db "w", "o", "r", ’d’, 0 ; defines a C string = "word"
L11 db ’word’, 0 ; same as L10
```

对于大量的数据序列，可以利用“TIMES”指示符。
```assembly
L12 times 100 db 0 ; equivalent to 100 (db 0)’s
L13 resw 100 ; reserves room for 100 words
```

标签（Label）可以在汇编代码中被使用。有两种使用方式：
1. 如果直接使用标签，代表数据的地址。
2. 如果用中括号括起标签，表示该标签处的数据是一个地址，要去找此地址所存的数据。（MASM/TASM使用不同的语法）

在32-bit模式下，一个地址有32-bit，例如：
```assembly
mov al, [L1] ; copy byte at L1 into AL
mov eax, L1 ; EAX = address of byte at L1
mov [L1], ah ; copy AH into byte at L1
mov eax, [L6] ; copy double word at L6 into EAX
add eax, [L6] ; EAX = EAX + double word at L6
add [L6], eax ; double word at L6 += EAX
mov al, [L6] ; copy first byte of double word at L6 into AL
```
最后一例展示了NASM的一个重要特性，汇编器并不知晓某个标签处数据的类型。所以要交由程序员正确地使用标签。
例如：
```assembly
mov [L6], 1 ; store a 1 at L6
```
这个语句会产生一个“operation size not specified”错误，因为汇编器并不知道要将1存储为一个字节、一个字、还是两个字。
改正如下：
```assembly
mov dword [L6], 1 ; store a 1 at L6
```
这告诉汇编器把1保存为双字长度的数据。（其它的说明符为byte、word、qword和tword——ten byte，浮点数处理用此数据类型）

#### 1.3.6 输入输出（Input and Output）
输入输出是极度依赖系统的活动，涉及与系统硬件的交互。
汇编语言没有像C语言那样的标准I/O库，故只能要么直接访问硬件（这在保护模式下需要操作权限），要么使用操作系统提供的低水平例程（low level routines）。

汇编例程（assembly routines）与C语言交互是非常常见的，这样做的一个优点是汇编代码可以使用C语言的标准库I/O例程。
然后在例程中给C语言传递信息的规则非常复杂，此处先不表。
为了简化，作者提供了他自己的例程，这些例程隐藏了复杂的C规则，提供了更简单的接口。（如下表所示）

|例程|描述|
|--|--|
| print_int | prints out to the screen the value of the integer stored in EAX|
| print_char |prints out to the screen the character whose ASCII value stored in AL|
|print_string| prints out to the screen the contents of the string at the address stored in EAX. The string must be a C type string (i.e. null terminated).|
|print_nl| prints out to the screen a new line character.|
|read_int| reads an integer from the keyboard and stores it into the EAX register.|
read_char| reads a single character from the keyboard and stores its ASCII code into the EAX register.|

所有的例程都保留（preserve）了所有寄存器的值，除了read例程。
这些例程确实改变了EAX寄存器的值。

要使用这些例程，必须包含一个头文件`%include "asm_io.inc"`（[asm io.inc](http://www.drpaulcarter.com/pcasm/)）。

使用任意一个print例程时，需要在EAX中加载入正确的值，并使用`call`指令来调用。

#### 1.3.7 调试（Debugging）
作者的库中也包含了很多用于调试程序的例程。这些例程可以显示计算机的当前状态信息，而不改变计算计的状态。这些例程实际上是一些保留当前CPU状态并调用子例程的宏。这些宏定义于`asm_io.inc`文件中（上文有提到）。宏的使用与其它指令一样，宏的操作数需要用逗号分隔。

有4个调试例程，分别名为：`dump_regs`（显示寄存器值）、`dump_mem`（显示内存值）、`dump_stack`（显示栈值）、`dump_math`（显示数学协处理器math coprocessor的值）。

### 1.4 创建程序（Creating a Program）
#### 1.4.1 
我们将从一个简单的C驱动程序开始（如下）
```c
int main()
{
  int ret_status ;
  ret_status = asm_main();
  return ret_status ;
}

```
此程序仅仅调用了asm_main函数而已，此函数是一个用汇编写的例程。

使用此C驱动程序有诸多优点：
1. 这让C系统驱动程序正确地在保护模式下运行，所以段和对应的段寄存器都通过C初始化，汇编语言不需要担心这些。
2. 同时，C库也可以被汇编代码所使用。

下面是要给简单的汇编程序：
```assembly
1 ; file: first.asm
2 ; First assembly program. This program asks for two integers as
3 ; input and prints out their sum.
4 ;
5 ; To create executable using djgpp:
6 ; nasm -f coff first.asm
7 ; gcc -o first first.o driver.c asm_io.o
8
9 %include "asm_io.inc"
10 ;
11 ; initialized data is put in the .data segment
12 ;
13 segment .data
14 ;
15 ; These labels refer to strings used for output
16 ;
17 prompt1 db "Enter a number: ", 0 ; don’t forget null terminator
18 prompt2 db "Enter another number: ", 0
19 outmsg1 db "You entered ", 0
20 outmsg2 db " and ", 0
21 outmsg3 db ", the sum of these is ", 0
22
23 ;
24 ; uninitialized data is put in the .bss segment
25 ;
26 segment .bss
27 ;
28 ; These labels refer to double words used to store the inputs
29 ;
30 input1 resd 1
31 input2 resd 1
32
33 ;
34 ; code is put in the .text segment
35 ;
36 segment .text
37    global _asm_main
38 _asm_main:
39    enter 0,0 ; setup routine
40    pusha
41
42    mov eax, prompt1 ; print out prompt
43    call print_string
44
45    call read_int ; read integer
46    mov [input1], eax ; store into input1
47
48    mov eax, prompt2 ; print out prompt
49    call print_string
50
51    call read_int ; read integer
52    mov [input2], eax ; store into input2
53
54    mov eax, [input1] ; eax = dword at input1
55    add eax, [input2] ; eax += dword at input2
56    mov ebx, eax ; ebx = eax
57
58    dump_regs 1 ; print out register values
59    dump_mem 2, outmsg1, 1 ; print out memory
60 ;
61 ; next print out result message as series of steps
62 ;
63    mov eax, outmsg1
64    call print_string ; print out first message
65    mov eax, [input1]
66    call print_int ; print out input1
67    mov eax, outmsg2
68    call print_string ; print out second message
69    mov eax, [input2]
70    call print_int ; print out input2
71    mov eax, outmsg3
72    call print_string ; print out third message
73    mov eax, ebx
74    call print_int ; print out sum (ebx)
75    call print_nl ; print new-line
76
77    popa
78    mov eax, 0 ; return back to C
79    leave
80    ret
```

第13行处定义了叫.data的数据段（data segment）——存放初始化的数据。
第26行处定义了叫.bss（block started by symbol）的数据段——存放未初始化的数据。
第36行定义了叫.text（叫此名是历史遗留）的代码段。
> 注意到“main程序例程”的代码标签有下划线作为前缀，用于标识C语言调用的代码段。（DOS/Windows系统专用，Linux没有这个传统）

第37行的`global`指示符告诉汇编器`_asm_main`是全局标签。默认情况下，一个汇编标签只能由相同的模块使用。添加了`global`指示符之后，任意一个模块都能使用该标签。
> `asm_io`中给`print_int`添加了`global`标签，故而`first.asm`可以使用该标签。

#### 1.4.2 编译器依赖（Compiler dependencies）
上面的代码适用于基于[GUN](http://www.fsf.org)的[DJGPP C/C++编译器](http://www.delorie.com/djgpp)。
需要386-based PC或者更好的版本，且要运行在DOS、Windows95/98或者NT下。
此编译器使用COFF（Common Object File Format）格式的目标文件。
要把用NASM汇编器把汇编文件汇编成此格式需要使用`-f coff`。结果会生成后缀为.o的目标文件。

Linux C编译器也是GNU编译器。想让上面的代码在Linux上运行，只要把诸如`_asm_main`处的下划线前缀删除就行了。  
Linux使用ELF（Executable and Linkable Format）格式的目标文件。对于该编译器使用`-f elf`来汇编。同样生成.o后缀的目标文件。

Borland C/C++是另一个流行的编译器。它使用微软OMF格式的目标文件。对于该编译器使用`-f obj`汇编。
OMF格式使用不同于其它格式的段指示符。
第13行的数据段需改为：
`segment DATA public align=4 class=DATA use32`
第26行的bss段需改为：
`segment BSS public align=4 class=BSS use32`
第36行的text段需改为：
`segment TEXT public align=1 class=CODE use32`
此外第36行之前应该添加一行代码：
`group DGROUP BSS DATA`

微软C/C++编译器同时支持OMF和Win32格式的目标文件（若是OMF格式，它会将其转化为Win32格式）。Win32格式允许像DJGPP和Linux那样去定义段。使用`-f win32`来汇编。后缀名为.obj。

#### 1.4.3 汇编代码（Assembling the code）
汇编代码第一步——在命令行输入：
```bash
nasm -f object-format first.asm
```
这里object-format的取值有coff、elf、obj或者win32。（记住对于Linux或者Borland需要修改源码）

#### 1.4.4 编译C代码（Compiling the C code）
用C编译器编译`driver.c`。
对于DJGPP：`gcc -c driver.c`。
`-c`表示只编译不链接（此开关对于Linux、Borland和微软编译器都适用）。

#### 1.4.5 链接目标文件（Linking the object files）
C代码需要标准C库（standard C library）和特殊的启动代码（startup code）才能运行。

DJGPP链接：
```bash
gcc -o first driver.o first.o asm io.o
# 生成first.exe（在Linux下为first）
```

Borland链接：
```bash
bcc32 first.obj driver.obj asm io.obj
# Borland以第一个目标文件的名字为可执行文件的名字
# 即生成first.exe
```

编译和链接可一步执行：
```bash
gcc -o first driver.c first.o asm io.o
```

#### 1.4.6 理解汇编清单文件（ Understanding an assembly listing file）

`-l listing-file`开关可以让NASM生成一个清单文件。此文件展示了代码是如何被汇编的。
下面是第17、18行的代码在清单文件中的样子：
```
48 00000000 456E7465722061206E- prompt1 db "Enter a number: ", 0
49 00000009 756D6265723A2000
50 00000011 456E74657220616E6F- prompt2 db "Enter another number: ", 0
51 0000001A 74686572206E756D62-
52 00000023 65723A2000
```
> 最左边是清单文件的行数——但不一定与源代码中的行数一致

第一列是行数；
第二列是数据的段内偏移量（16进制）；
第三列是将被存储的数据的16进制形式；
最后一列展示了源代码。

第二列所列出的数据段内偏移量非常有可能不是最终完整程序的数据段内偏移量。
每个模块都会定义自己的数据段标签，故而在链接阶段，所有的数据段标签会合并为一个数据段。最终得到的偏移量由链接器计算。

第54行到56行源代码在清单文件中的样子：
```
94 0000002C A1[00000000] mov eax, [input1]
95 00000031 0305[04000000] add eax, [input2]
96 00000037 89C3 mov ebx, eax
```

第三列展示了汇编器生成的机器语言。
通常指令的完整代码在这时还无法被计算。
比如94行处，在链接之前无法得知input1的偏移量。
汇编器可以计算mov指令的操作码（此处为A1），但将偏移量用中括号包裹起来，因为确切数值还无法计算。
在这种情况下，临时的偏移量为0，因为input1是在bss段的开头位置。
当链接器链接时，正确的偏移量会被插入到这个位置。
像96行这样的指令的完整机器码可以被计算出来，因为此指令不涉及任何标签。

##### 大小端（Big and Little Endian Representation）
仔细看95行可能会觉得奇怪，input2标签定义在此文件的偏移量为4，但为何在内存中的表示不是00000004而是04000000呢？

不同处理器以不同次序存储内存中的多字节整数。

大端：大数在左，小数在右。如00000004存储为`00 00 00 04`。
IBM大型机、多数RISC处理器和Motorola处理器都使用大端存储。

小端：小数在左，大数在右。如00000004存储为`04 00 00 00`。
Intel-based处理器使用此方式。这种方式是硬件层面决定的。

大多数时候程序员无需关心大小端，但以下场景有必要关心：
1. 二进制文件在不同电脑间进行传输（无论是通过文件还是网络）；
2. 当二进制数据以多字节整数形式写入内存，而又通过单字节形式读取时（或者反过来）。

### 1.5 框架文件（Skeleton File）
```
%include "asm_io.inc"
2 segment .data
3 ;
4 ; initialized data is put in the data segment here
5 ;
6
7 segment .bss
8 ;
9 ; uninitialized data is put in the bss segment
10 ;
11
12 segment .text
13    global _asm_main
14 _asm_main:
15    enter 0,0 ; setup routine
16    pusha
17
18 ;
19 ; code is put in the text segment. Do not modify the code before
20 ; or after this comment.
21 ;
22
23    popa
24    mov eax, 0 ; return back to C
25    leave
26    ret
```
此文件可以作为写汇编程序的框架。