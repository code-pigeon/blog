# sublime text笔记
## 一般快捷键
`ctrl`+`P`：通过查找跳转到目录下任意文件；
`ctrl`+`shift`+`P`：通过查找使用快捷键；
`ctrl`+`M`：跳转到匹配的括号处；
`ctrl`+`G`：跳转到行；
`alt`+`数字`：跳转到对应位置的标签页；
`ctrl`+`PgUp/PgDn`：按顺序切换标签页；

## 查找与替换
`ctrl`+`F/H`：查找/替换；

在查找下的快捷键：
`alt`+`R`：正则表达式开关；
`alt`+`C`：大小写开关；
`alt`+`W`：精确匹配开关；
`enter`：查找下一个；
`shift`+`enter`：查找上一个；
`alt`+`enter`：查找全部；

## 
`ctrl`+`R`：查找函数；
`ctrl`+`;`：查找；

## 
`ctrl`+`X`：删除行；
`ctrl`+`enter`：行后插入行；
`ctrl`+`shift`+`enter`：行前插入行；
`ctrl`+`L`：选中行；
`ctrl`+`shitf`+`J`：合并行；
`ctrl`+`shift`+`/`：块注释；
`ctrl`+`shift`+`V`：粘贴并自动缩进；

## snippet
snippet：文件后缀`.sublime-snippet`的xml文件。
> 若想要在`<content>`标签中写`$`应该写`\$`。
```xml
<snippet>
  <content><![CDATA[<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="description" content="$1">
    <meta name="viewport" content="width=device-width, initial scale=1">
    <title>${2:Untitled}</title>
  </head>
  <body>
    Hello ${3:$TM_FULLNAME}! Welcome to $2!
    $0
  </body>
</html>]]>
  </content>
  <tabTrigger>doctype</tabTrigger>
  <description>HTML5 Structure</description>
  <scope>text.html</scope>
</snippet>
```
tabTrigger：触发snippet的关键字；
scope：表示此snippet的作用范围（文件类型），scope的完整类型见[https://gist.github.com/danpe/6993237](https://gist.github.com/danpe/6993237)；Hello you are sb!

触发此snippet之后，首先光标会到达`content="$1"`的`$1`处；
然后会到`${2:Unititled}`处，此处的默认值为`Untitled`；
接着会到`${3:$TM_FULLNAME}`处，此处的`$TM_FULLNAME`为环境变量，对于完整的环境变量见[https://gist.github.com/danpe/6996806](https://gist.github.com/danpe/6996806)；
最后退出snippet时，光标会到`$0`处，若没有`$0`，则默认跳转到snippet的最后。
