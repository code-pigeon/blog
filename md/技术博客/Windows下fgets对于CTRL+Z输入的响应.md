# Windows下fgets对于CTRL+Z输入的响应
首次编辑：2024/6/30/14:49
最后编辑：2024/7/18

## Windows下CTRL+Z在标准输入中的作用
程序读入文件需要用一个“文件结束符”（通常记作`EOF`，即“End of File”）来标记文件的结尾，标准输入作为一个特殊的文件，同样也有它的`EOF`，它就是`ctrl + z`。

在终端按下`ctrl`键，然后再按下`z`键即可以输入`EOF`，在终端会显示`^Z`，但它实际上和手动输入的`^`加上`Z`并不相同，前者为1个字符，后者为两个字符。

但在使用C标准库的`fgets`读入一行命令行输入时，却发现`ctrl + z`并不总是会解释为`EOF`。

在键入`ctrl + z`之前如果没有其它字符，才会被解释为`EOF`，若`ctrl + z`之前有其它字符，`fgets`根本不会结束，反而会继续等待用户输入。

## 循环读入用户输入的例子
```c
char buf[64];

printf(">> ");
while(fgets(buf, sizeof(buf), stdin)){
	printf("你输入的是：");
	puts(buf);
	printf(">> ");
}

if( feof(stdin)){
	printf("文件到达末尾");
}
```
在这个例子中，每次用户输入之前程序会输出提示符">> "提示用户输入内容。

如果输入常规的字符，`fgets`会立即结束，并输出读入的字符串。
```
>> jkl
你输入的是：jkl

>> 
```

只输入`ctrl + z`，`fgets`会结束，并返回`NULL`，使得循环结束。
```
>> ^Z
文件到达末尾
```

但若先输入其它字符，再输入`ctrl + z`，`fgets`不会返回，而会继续等待用户输入。
```
>> jkl^Z

```
如果继续接入普通字符，并按下回车，会获得下面输出：
```
>> jkl^Z
jkl
你输入的是：jkl␦jkl

>> 
```
`ctrl + z`就对应那个镜像的问号“␦”。

为了看看这其中到底发生了啥，还是需要直接查看字符的ascii值。

## 观察不同情况下`ctrl + z`对应字符的ascii值
```c
void print_buf_as_hex(char* p){
	printf("\n");
	while( *p ){
		printf("%x ",*p++);
	}
	printf("\n");
}

int main(){
	char buf[64];

	printf(">> ");
	while(fgets(buf, sizeof(buf), stdin)){
		printf("你输入的是：");
		print_buf_as_hex(buf);
		printf(">> ");
	}

	if( feof(stdin)){
		printf("文件到达末尾");
	}
	return 0;
}
```

首先是普通的输入：
```
>> jkl
你输入的是：
6a 6b 6c a
>>
```
`6a 6b 6c`对应`jkl`的ASCII值，后面的`a`对应换行符`\n`。

单独的`ctrl + z`：
```
>> ^Z
文件到达末尾
```
这种情况循环直接被跳过了，所以没有输入ascii值（不过非要看也是可以的，只不过`EOF`并不会被`fgets`读到`buf`中，所以不看也罢）。

先输入“jkl”再输入`ctrl + z`：
```
>> jkl^Z
jkl
你输入的是：
6a 6b 6c 1a 6a 6b 6c a
>>
```
两处`6a 6b 6c`对应两处`jkl`，但它们中间却是个十六进制的`1a`。

去查一下ASCII表，十六进制`1a`对应的是控制符`sub`（substitute），咱也不知道是啥作用。
> 引用chatgpt：
ASCII 码中十六进制为 1A 的值表示 Substitute，通常缩写为 SUB。这个字符在 ASCII 控制字符中具有特定的含义：
- ASCII 控制字符：1A 是 ASCII 表中的一个控制字符，通常用于表示替换字符或作为文件传输中的特殊标记。
- 功能：在文本处理中，SUB 通常用于表示不可打印字符或用于特殊用途，例如在早期的计算机和通信设备中，可能用于指示数据流的中断或结束。
总之，ASCII 十六进制为 1A 的值 SUB 表示替换字符，其具体的使用取决于特定的应用和上下文。

在一个[网友的博客](https://blog.csdn.net/i6223671/article/details/89041492)下找到了答案：
> windows下的ctrl+z用来作为结束输入输出流的标值，控制台读入字符^Z，只有另起一行放在行首才会起作用，否则表示结束本行……

## 常见的解释性语言对此问题的处理
结论已经有了，`ctrl + z`只有放在行首时才表示`EOF`，于是我想到了各大解释性语言对这个问题的处理，像python、lua甚至是java的交互式命令行工具jshell。

### python
实验结果发现python非常的智能：
```
>>> jkl^Z
  File "<stdin>", line 1
    jkl␦
       ^
SyntaxError: invalid non-printable character U+001A
>>>
```
读到`ctrl + z`之后直接就报错了。

### lua
相比之下，lua就逊色一些，表现和我们的实验一模一样，似乎它的交互式命令行就是用`fgets`写的：
```
> jkl^Z

(这是在第二行等待输入)
```

继续输入之后：
```
> jkl^Z
jkl
stdin:1: syntax error near '<\26>'
> 
```

### jshell
jshell就很霸气，直接禁用了`ctrl + z`（根本无法输入这个字符）。

然后我就在思考jshell用什么退出呢，试了一下`ctrl + d`（Linux的`EOF`），果不其然马上退出了。

但如果先输入字符再输入`ctrl + d`就没用了，输入任意字符之后`ctrl + d`会被禁用。