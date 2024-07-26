[《PC Assembly Language》](http://pacman128.github.io/static/pcasm-book.pdf)[Paul A. Carter](http://pacman128.github.io/)
## 第3章-位操作Bit Operations
### 3.1 位移（Shift Operations）
#### 3.1.1 逻辑位移（Logical shifts）
逻辑位移中，新增的bit位总是0。
```
逻辑右移：
			0101011
shr 1 -->	0010101

逻辑左移：
			0101011
shl 1 -->	1010110

```
在汇编语言中，用`shr`和`shl`来执行逻辑位移操作。
位移的位数可以是立即数，也可以是存放在`CL`寄存器中的数字。

最后一个被移出的bit位会被存入进位标志位（carry flag）中。

```assembly
mov ax, 0C123H
shl ax, 1 ; shift 1 bit to left, ax = 8246H, CF = 1
shr ax, 1 ; shift 1 bit to right, ax = 4123H, CF = 0
shr ax, 1 ; shift 1 bit to right, ax = 2091H, CF = 1
mov ax, 0C123H
shl ax, 2 ; shift 2 bits to left, ax = 048CH, CF = 1
mov cl, 3
shr ax, cl ; shift 3 bits to right, ax = 0091H, CF = 1
```

> 位移操作速度比`mul`和`div`快得多，而乘法和除法又可以通过位移实现。
故可以用逻辑位移实现**无符号数**的乘法和除法。


#### 3.1.3 算术位移（Arithmetic shifts）
- `sal`：就是`shl`，一模一样；
- `sar`：新增加的比特位将会和符号位保持一致。

#### 3.1.4 循环位移（Rotate shifts）


### 3.2 布尔位操作（Boolean Bitwise Operations）
#### 3.2.1 与（The AND operation）
```assembly
mov ax, 0C123H
and ax, 82F6H ; ax = 8022H
```
#### 3.2.2 或（The OR operation）
```assembly
mov ax, 0C123H
or ax, 0E831H ; ax = E933H
```

#### 3.2.3 亦或（The XOR operation）
```assembly
mov ax, 0C123H
xor ax, 0E831H ; ax = 2912H
```

#### 3.2.4 取反（The NOT operation）
不同与上面的指令，取反指令是一元操作（只有一个操作数），且不会影响FLAGS寄存器的数值
> 意思是其它指令都会影响FLAGS寄存器的数值

```assembly
mov ax, 0C123H
not ax ; ax = 3EDCH
```

#### 3.2.5 测试（The TEST instruction）
同`and`指令，但是不存储计算结果，只根据结果修改FLAGS寄存器的数值。
> 比如结果为0时，ZF会被置为1。

#### 3.2.6 布尔操作的用途（Uses of boolean operations）
##### 主要用途
- 将第i位置为1：与2的i次方（此数字的2进制只有第i位是1）进行`or`操作；
- 将第i位置为0：与只有第i位是0的2进制数（此数通常称为掩码，mask）进行`and`操作；
- 对第i位取反：与2的i次方（此数字的2进制只有第i位是1）进行`xor`操作；

```assembly
mov ax, 0C123H
or ax, 8 ; turn on bit 3, ax = C12BH
and ax, 0FFDFH ; turn off bit 5, ax = C10BH
xor ax, 8000H ; invert bit 31, ax = 410BH
or ax, 0F00H ; turn on nibble, ax = 4F0BH
and ax, 0FFF0H ; turn off nibble, ax = 4F00H
xor ax, 0F00FH ; invert nibbles, ax = BF0FH
xor ax, 0FFFFH ; 1’s complement, ax = 40F0H
```
> nibble表示4位2进制数，即一个16进制数。

##### 其它用途

1. `and`指令还可以用于计算以2的i次方作为除数的除法的余数。
> 即a/b = c..d，b=2^i，可以用`and`计算d

方法：被除数与数值上等于2^i-1的掩码相与，相与结果就是余数。
例如：
```assembly
mov eax, 100 ; 100 = 64H 被除数为100
mov ebx, 0000000FH ; mask = 16 - 1 = 15 or F  除数为16，掩码为16-1 = 15，写成16进制就是F
and ebx, eax ; ebx = remainder = 4 
shr eax, 4 ; eax = quotient of eax/2^4 = 6
```

2. 使用CL寄存器可以操作任意数量的任意位。

例1：将EAX中的任意一个位置为1，此位的位置存放在BH中。
```assembly
mov cl, bh ; first build the number to OR with
mov ebx, 1
shl ebx, cl ; shift left cl times
or eax, ebx ; turn on bit
```

例2：将EAX中的任意一个位置为0，此位的位置存放在BH中。
```assembly
mov cl, bh ; first build the number to AND with
mov ebx, 1
shl ebx, cl ; shift left cl times
not ebx ; invert bits
and eax, ebx ; turn off bit
```

##### 一段奇怪的代码
```assembly
xor eax, eax ; eax = 0
```
此代码用于将eax清零，因为任何数与自己亦或都是0。
之所以不用`mov eax 0`来清零是因为`xor`的机器码占用的字节数更短。

### 3.3 C语言的位操作（Manipulating bits in C）

### 3.4 大小端表示（Big and Little Endian Representations）
x86家族使用小端表示法。