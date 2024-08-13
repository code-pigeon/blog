# Linux终端控制
首次编辑：2024/6/10/13:21  
最后编辑：2024/6/10/18:50

## 从在终端输出彩色字符开始
以前还不知道怎么在终端输出彩色的字符，直到后来知道了输出像`\033[30m`这样的字符可以改变字体的颜色。
> 目前知道在python里的`print`和C语言中的打印函数打印该字符串都可以改变字体颜色，其它语言还没试过。

其中`30`表示黑色，从30到37都代表了不同的颜色：
```comment
Black       0;30     Dark Gray     1;30
Blue        0;34     Light Blue    1;34
Green       0;32     Light Green   1;32
Cyan        0;36     Light Cyan    1;36
Red         0;31     Light Red     1;31
Purple      0;35     Light Purple  1;35
Brown       0;33     Yellow        1;33
Light Gray  0;37     White         1;37
```
感觉长得有点不一样？是的，`\033[30m`其实是`\033[0;30m`的缩写，对应上面的黑色。

但其实前面的这个0和1更像是开关，在第一次打印`\033[1;30m`之后，再打印`\033[37m`将会得到“White”而不是“Light Gray”。也就是说此时的`\033[37m`已经变成了`\033[1;37m`的缩写。

但很快对这件事情的认识又有了新的进展。
不仅仅是0和1，还可以一直写到5……而且不仅字体颜色可以改变，还可以改变背景颜色。
在这里直接偷一张[别的网站](https://stackabuse.com/how-to-print-colored-text-in-python/)的图：
![打印彩色字体格式](https://stackabuse.s3.amazonaws.com/media/how-to-print-colored-text-in-python-01.jpg)
> 更丰富的字体效果就去这个网站里看看吧。

至于这个效果嘛，Windows cmd和Linux终端还是不太一样的。cmd没有发现闪烁功能，但Linux终端有。

最后来看看这玩意儿的名字，为啥叫escape sequences？

我在stack exchange的一个[帖子](https://askubuntu.com/questions/831971/what-type-of-sequences-are-escape-sequences-starting-with-033)上看到了疑似的答案：

> ... the builtin echo command accepts \033 as a representation of the ESC character.

所以这个神秘的`\033`其实就是键盘上左上角那个`Esc`键（的ASCII值的八进制表示）。

## Linux终端控制字符
随着了解的深入，我发现所谓的“escape sequences”不仅仅是改变字体和背景色这么简单，诸如光标移动、文本格式等都可以通过“escape sequences”来进行控制。

而前文所涉及到的只是“escape sequences”的一个部分（不过也是最庞大的一部分），叫做CSI（Control Sequence Introducer），它们的共同特点是都以`\033[`（即`ESC[`）开头。其它的“escape sequences”也都以`\033`开头。

而除了ESC字符所涉及到的“escape sequences”之外，还有其它的一些字符也都用于终端控制。

总结一下就是，CSI序列 ∈ ESC序列 ∈ Linux终端控制。

详细的内容可以参考[console_codes(4)——Linux manual page](https://man7.org/linux/man-pages/man4/console_codes.4.html)
> 这里需要吐槽一下Linux manual page的书写风格，譬如
> 
> > A   CUU       Move cursor up the indicated # of rows.
> 
> 这里的“#”实际上指的是number，也就是将光标向上移动#行。
>
> 而且CUU仅仅只是个助记符，不是参数，所以在Linux终端上实现向上移动光标的指令是`echo -e "\033[20A"`。是的，这是向上移动20行。
> 
> 基于以上吐槽，建议参考[ANSI/VT100 Terminal Control Escape Sequences](https://www2.ccs.neu.edu/research/gpc/VonaUtils/vona/terminal/vtansi.htm)或者[Bash Prompt HOWTO](https://tldp.org/HOWTO/Bash-Prompt-HOWTO/c327.html)

## 最后看看两个概念
在观看参考资料的时候发现了一些令人讨厌的东西，什么“ECMA-48”和“VT102”。

后来了解了一下，“ECMA-48”就是一个终端控制的标准，而“VT102”则是这个标准的具体实现。此外还有一个叫“VT100”的实现，这是一个更早更简单的实现。VT102兼容VT100，但功能更加丰富。
