[《PC Assembly Language》](http://pacman128.github.io/static/pcasm-book.pdf)[Paul A. Carter](http://pacman128.github.io/)
## 第2章-基础汇编语言Basic Assembly Language
### 2.1 使用整型（Working with Integers）
#### 2.1.1 整型的表示（Integer representation）
unsigned integers；
signed integers：
- signed magnitude（原码）
- one's complement（反码）
- two's complement（补码）

#### 2.1.2 符号扩展（Sign extension）
##### 缩短数据长度（Decreasing size of data）
直接丢弃高位数据即可：
```assembly
mov ax, 0034h ; ax = 52 (stored in 16 bits)
mov cl, al ; cl = lower 8-bits of ax
```
若该数据无法用更小的长度表示，这种转化就会出现错误。

对于无符号数，当丢弃的高位全为0时，转化就是正确的；
对于有符号数，丢弃的高位全为0或者全为1，且第一个不被丢弃的位与被丢弃的位的值一样时，转化才是正确的。

##### 增加数据长度（Increasing size of data）
对于无符号数，直接在高位补0即可；
对于有符号数，若符号位为0，则高位补0，若符号位为1，则高位补1；

80386提供了许多数字扩展指令。
> 记住计算机并不知道数据是否有符号，这都需要程序员自己去考虑。


**对于无符号数**，可以直接用`mov`指令把0传入高位比特。
例如，将AL中的一个字节扩展为AX的一个字：
```assembly
mov ah, 0 ; zero out upper 8-bits
```

但无法用`mov`指令将AX中的一个字长度的无符号数转化为EAX中的双字长度的无符号数。
这是因为没有办法直接访问EAX的高16位。

为解决此问题，80386提供了`movzx`指令，此指令接收两个操作数：第一个操作数（目的操作数，destination）是16-bit或者32-bit的寄存器；第二个操作数（源操作数，source）可以是8-bit或16-bit寄存器，也可以是1字节或1个字的内存。
另外此指令要求目的操作数的长度必须大于源操作数（多数指令要求两操作数长度相等）

例如：
```assembly
movzx eax, ax ; extends ax into eax
movzx eax, al ; extends al into eax
movzx ax, al ; extends al into ax
movzx ebx, ax ; extends ax into ebx
```

**对于有符号数**，用`mov`无法实现扩展。

但8086提供了一些指令扩展有符号数。
|指令|翻译|描述|
|--|--|--|
|CBW|Convert Byte to Word|将AL扩展为AX|
|CWD|Convert Word to Double word|将DX扩展为DX:AX|

> 记住8086没有32位寄存器。所以只能将DX:AX两个16-bit寄存器看成一个32-bit寄存器。

80386增加了一些指令扩展有符号数。
|指令|翻译|描述|
|--|--|--|
|CWDE|Convert Word to Double word Extended|将AX扩展为EAX|
|CDQ|Convert Double word to Quad word|将EAX扩展为EDX:EAX|
|MOVSX||（像MOVZX那样工作，但是针对有符号数）

##### 应用到C语言（Application to C programming）
**例1**
```c
unsigned char uchar = 0xFF;
signed char schar = 0xFF;
int a = (int ) uchar; // a = 255 (0x0000FF)
int b = (int ) schar ; // b = −1 (0xFFFFFFFF)
```
> ANSI C并没有规定char类型是有符号的还是无符号的，故交由不同编译器去决定这一点。这就是为什么在此例中显式地定义了char类型有无符号。

在此例中，第三行的数据运用了无符号数的扩展规则扩展（movzx），第四行用有符号数的规则扩展（movsx）。

**例2**
```c
char ch;
while( (ch = fgetc(fp )) != EOF ) {
	// do something with ch
}
```
这段代码暗含一个常见bug。

`fgetc`的函数原型（prototype）是：
```c
int fgetc( FILE * );
```
可是`fgetc`读的明明是字符，为什么返回`int`呢？
原因是通常fgetc确实返回字符，但当读到文件结尾时，它就会返回一个EOF宏（通常定义为-1）。所以`fgetc`要么返回一个由char扩展而来的int（在16进制下为000000xx），要么返回EOF（在16进制下为FFFFFFFF）。

fgetc返回int，但在例2中却用char类型存储这个int。C语言在这时会将int的高位截断。问题在于`000000FF`和`FFFFFFFF`都会被截断为`FF`，while循环的判断如何区分这两者呢。

关键在于，char类型是否有符号。
在while循环的判断中，ch与EOF作对比。因为EOF是int类型值，所以为了与EOF比较，ch会被扩展为int（这样两者才拥有相同长度）。

若char是无符号的，`FF`就会被扩展为`000000FF`，与EOF（即`FFFFFFFF`）进行比较，发现不相等。于是while循环永不终止！

若char是有符号的，`FF`就会被扩展为`FFFFFFFF`。如此一来，循环可以终止，但新的问题是，`FF`也可能是由某个不是EOF的字符截断而来，这样就无法保证只有读到文件结尾时才终止循环。

所以应该将ch定义为char类型而非int类型，才不会出现上述问题。

#### 2.1.3 补码运算（Two’s complement arithmetic）
##### 加减运算
`add`指令用于加法，`sub`指令用于减法。
这两个指令的执行将会影响标志寄存器中的溢出位（overflow）和进位（carry flag）的值。
当计算结果太长时，溢出位将被置为1；当做加法时最高位（msb）有进位或做减法时最高位有借位时，进位将被置为1。
所以这两个标志位可以用于检测无符号运算时是否有溢出。
用补码运算时，加法与减法规则与无符号运算完全一致。
所以`add`和`sub`可以用于有符号和无符号的整数运算。

##### 乘法运算
`mul`用于计算有符号整数乘法；
`imul`用于计算无符号整数乘法。
> FF这个1字节的数据，在有符号数中是255，无符号数中是-1。若两个FF相乘，有符号数情况下将得到255×255=65025（八进制为FE01）；无符号数情况下将得到-1×-1=1（八进制为0001）。所以需要不同的指令处理这两种情况。

乘法指令有很多形式，最古老的形式为：
`mul source`
> source可以是寄存器或内存，但不能为立即数。

- 若操作数为1B长度，则与AL寄存器的值相乘，结果存储在2B的AX中
- 若操作数为2B长度，则与AX相乘，结果存储在DX:AX中。
- 若操作数为4B长度，则与EAX相乘，结果存储在EDX:EAX中。

`imul`指令的格式与`mul`相似，还增加了2操作数和3操作数格式。

```assembly
imul dest, source1
imul dest, source1, source2
```

下表是可能的组合：
|dest |source1 |source2 |Action|
|-----|--|--|--|
||reg/mem8 ||AX = AL×source1|
||reg/mem16 ||DX:AX = AX×source1|
||reg/mem32 ||EDX:EAX = EAX×source1|
|reg16|reg/mem16 ||dest ×= source1
|reg32|reg/mem32 ||dest ×= source1|
|reg16|immed8 ||dest ×= immed8|
|reg32|immed8 ||dest ×= immed8|
|reg16|immed16 ||dest ×= immed16|
|reg32|immed32 ||dest ×= immed32|
|reg16|reg/mem16 |immed8 |dest = source1×source2|
|reg32|reg/mem32 |immed8 |dest = source1×source2|
|reg16|reg/mem16 |immed16 |dest = source1×source2|
|reg32|reg/mem32 |immed32 |dest = source1×source2|

##### 除法运算
有符号数：`div`；
无符号数：`idiv`。

格式为：`div source`。

- 若source为1B，执行AX/source，商存于AL中，余数存于AH。
- 若source为2B，执行DX:AX/source，商存于AX，余数存于DX。
- 若source为4B，执行EDX:EAX/source，商存于EAX，余数存于EDX。

`idiv`的格式与`div`相同。

> 若商太大了，寄存器无法存放，或者除数为0，程序将中断并终止。
一个常见的错误是做除法前忘记初始化DX或EDX。

##### 取倒数运算
`neg operand`，operand可以是1B、2B、4B寄存器者内存。

#### 2.1.5 扩充精度运算（Extended precision arithmetic）
长度大于4B的数据的加减法需借助指令：`adc`和`sbb`。
`adc`计算原理：
> opreand1 = operand1 + carry flag + operand2

`sbb`：
> operand1 = operand1 - carry flag - operand2

计算方法：
若参与计算的8B整型值分别存储在EDX:EAX和EBX:ECX中
则
```assembly
add eax, ecx ; add lower 32-bits
adc edx, ebx ; add upper 32-bits and carry from previous sum
```
将计算出其和并存储在EDX:EAX中；

```assembly
sub eax, ecx ; subtract lower 32-bits
sbb edx, ebx ; subtract upper 32-bits and borrow
```
将计算EBX:ECX - EDX:EAX并存储在EDX:EAX中.

对于更长的数字，可以使用循环，在循环中使用`adc`指令来计算和差。
可以在循环开始前使用`clc`（CLear Carry）指令来清空进位。当进位为0时，`add`与`adc`指令的效果是相同的。
同样的思想可以运用于减法。

### 2.2 控制结构（Control Structures）
#### 2.2.1 比较（Comparisons）
`cmp A B`执行A-B，但不会保存结果，只根据结果修改标志寄存器内容。

- 对于无符号数：（当减法有借位时，CF就会置1）
	- 若A=B，ZF = 1、CF = 0
	- 若A>B，ZF = 0、CF = 0
	- 若A\<B,ZF = 0、CF = 1
- 对于有符号数：（影响SF，signed flag、OF，overflow flag）
	- 若A=B，ZF = 1
	- 若A>B，ZF = 0、SF = OF
	- 若A\<B,ZF = 0、CF =/= OF

> 别忘了其它指令也能改变标志寄存器信息。

#### 2.2.2 分支指令
|分支指令类型|描述|
|--|--|
|JMP \[code label\]|无条件跳转|
|JZ | branches only if ZF is set|
|JNZ | branches only if ZF is unset|
|JO | branches only if OF is set|
|JNO | branches only if OF is unset|
|JS | branches only if SF is set|
|JNS | branches only if SF is unset|
|JC | branches only if CF is set|
|JNC | branches only if CF is unset|
|JP | branches only if PF is set|
|JNP | branches only if PF is unset|
> PF（parity flag）为奇偶标志位。


`short jmp \[code label\]`：只可以向前/后跳转128B，因为它只用1个有符号的字节记录跳转位移。

`near \[分支类型指令\] \[code label\]`：就是默认的跳转类型，可以跳转至内存中的任何位置。

`far \[分支类型指令\] \[code label\]`：可以跨端跳转（几乎用不着）

同时还有一些更易读的指令：
|Signed|Unsigned|
|--|--|
|JE branches if vleft = vright| JE branches if vleft = vright|
|JNE branches if vleft != vright| JNE branches if vleft != vright|
|JL, JNGE branches if vleft < vright| JB, JNAE branches if vleft < vright|
|JLE, JNG branches if vleft ≤ vright| JBE, JNA branches if vleft ≤ vright|
|JG, JNLE branches if vleft > vright| JA, JNBE branches if vleft > vright|
|JGE, JNL branches if vleft ≥ vright| JAE, JNB branches if vleft ≥ vright|

#### 2.2.3 循环指令（The loop instructions）
80x86提供了很多实现类似for循环的指令，它们都接收一个代码标签作为唯一的操作数。
- `loop`：ECX中的数值减1，若ECX≠0，跳转到标签处；
- `loope`、`loopz`：ECX中的数值减1（FLAGS寄存器不会被修改），若ECX≠0且ZF=1，跳转；
- `loopne`、`loopnz`：ECX中的数值减1（FLAGS寄存器不会被修改），若ECX≠0且ZF=0，跳转；

后两条指令擅长顺序搜索循环，例如：
```c
sum = 0;
for( i=10; i >0; i−− )
	sum += i;
```
可以转化为
```assembly
	mov eax, 0 ; eax is sum
	mov ecx, 10 ; ecx is i
loop_start:
	add eax, ecx
	loop loop_start
```