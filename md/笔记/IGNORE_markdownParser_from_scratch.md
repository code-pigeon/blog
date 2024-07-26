# 从零开始写一个简易的markdown解析器
这是面向对象课程的大作业，需要使用设计模式完成这个作业。
对于怎么完成这个作业自己的思想斗争挺多的。

- cv工程？主要怕被认出来，更怕同学和我抄到一样的。
- 从使用的设计模式出发，寻找能用上这些设计模式的实际问题？感觉大多数人应该是这么做的，这样子水起来很容易，问题是感觉很浪费时间，首先这个强扭出来的实际问题，肯定不会自己感兴趣的，既然是要水，却在一个自己不感兴趣的问题上花时间，过后很可能自己马上忘了，以后也永远不会用到，这样算起来，花的这些时间显然是亏的。

所以我选择从自己感兴趣的问题出发，寻找能用上什么设计模式，也许这样完成作业所耗费的时间比较值得。

很想自己写个markdown解析器，如果能够自己写解析器，那么就能够自定义解析后的效果（虽然看开源的东西好像也能达到同样的效果）。

开发过程中将会使用一些TDD（Test Drive Development）的思想，久闻大名，但从来没有在开发中应用过的开发方式。
TDD的具体方式其实我也不知道，也许是要先写测试类？

[2023-12-12/15:21]

## 一、开始
解析markdown，那解析类就叫`MarkdownParser`吧。

因为需要使用TDD开发方式，需要搞个`MainTest`类。

`MarkdownParser`类和`MainTest`类分别丢进`entity`包和`test`包中。

目前项目文件夹如下：
```
\src
|
+-- Main.java
|
+--\entity
|  |
|  +-- MarkdownParser.java
|
+--\test
   |
   +-- MainTest.java

```

首先开撸测试类，先创建`MarkdownParser`类，然后创建测试用的markdown文本，接着用`MarkdownParser`类解析markdown文本，再测试一下和预期文本一不一样。

应该就是这样了。

```java
// MainTest.java
public class MainTest {
    public static void main(String[] args) {
        MarkdownParser markdownParser = new MarkdownParser();

        String markdown_text = "# 哈哈\nThis is a **test**. \n";
        String html_text = markdownParser.parse(markdown_text);
        System.out.println("解析结果为：" + html_text);


        if (Objects.equals(html_text, "<h1>哈哈</h1>\n<p>This is a <b>test</b>. </p>\n")){
            System.out.println("成功！");
        }else {
            System.err.println("错误！");
        }
    }
}

```

此时`MarkdownParser`类还没有编写，进入`MarkdownParser.java`文件中，给它上点东西：
```java
public class MarkdownParser {
    public String parse(String markdown_text) {  // 解析md文本
        String html_text = "";

        return html_text;
    }
}
```

当然此时的`MarkdownParser`类的`parse`方法还没有任何实质意思的实现。

此时运行`MainTest`的`main`方法，测试肯定是不通过的：
```
解析结果为：
错误！
```

## 二、白嫖一个设计模式
其实很没必要，但我觉得还是要用一下，不然设计模式可能达不到作业要求了。
但其实也挺适合的，因为无论多少markdown文本，也只需要同一个解析器解析就行了。

### 给MarkdownParser上个单例模式
给`MarkdownParser`类添加点东西（没改变的东西省略不写了）。
```java
public class MarkdownParser {

	// ========================= 单例模式的实现 =================================================
    private final static MarkdownParser INSTANCE = new MarkdownParser();  // 将类实例定义为类变量
    private MarkdownParser() {}  // 只允许类中调用，防止外部调用
    public static MarkdownParser getInstance() {  // 获取全局唯一的类实例
        return INSTANCE;
    }
    // =========================================================================================


    public String parse(String markdown_text) {  // 解析md文本
        //...
    }
}

```

随之`MainTest`方法也要改改：
```java
public class MainTest {
    public static void main(String[] args) {
    	// 原来的代码：MarkdownParser markdownParser = new MarkdownParser();
        MarkdownParser markdownParser = MarkdownParser.getInstance();  

        // ... 
    }
}

```

## 三、开始真正地解析markdown

### 分行
首先markdown文本应该拆成一行一行来解析，所以`parse`方法的第一步应该是分行：
```java
public class MarkdownParser {
    // ... 

    public String parse(String markdown_text) {  // 解析md文本
        String html_text = "";  // 最终要返回的html文本
        for (String line : markdown_text.split("\n")){  // 将md文本分行，每次单独处理一行
            // 解析一行md文本
            // 将解析得到的html文本追加到变量“html_text”上
        }
        return html_text;
    }
}

```

`for`循环中的注释表明了我们需要对每一行md文本做的事情。

注释中要做的事情应该交给一个新的函数来实现了，不然阅读应该挺困难的。
根据它的功能，我觉得这个函数或许可以叫`parseMarkdownLine`？怪怪的，但先这么命名吧。

> 随便把`parse`方法重命名为`parseMarkdown`了，意义更明确一点。

```java
public class MarkdownParser {
    // ...

    public String parseMarkdown(String markdown_text) {  // 解析md文本
        String html_text = "";  // 最终要返回的html文本
        for (String markdown_line : markdown_text.split("\n")){  // 将md文本分行，每次单独处理一行
            String html_line = parseMarkdownLine(markdown_line);  // 解析一行md文本
            html_text = html_text + html_line;  // 将解析得到的html文本追加到变量“html_text”上
        }
        return html_text;
    }

    private String parseMarkdownLine(String markdownLine) {  // 添加解析单行md的方法
        String html_line = "";
        return html_line;
    }
}
```

接下来就把精力放在如何解析实例文本“# 哈哈\nThis is a \*\*test\*\*. \n”了。


### 解析一级标题
markdown中的一级标题所使用的语法是
```markdown
# Title
```
所以可以用`String`的`startsWith`方法判断是不是以“#”开头的，如果是，再使用`String`的`split`方法，把“#”和“Title”分开，只保留后面的“Title”，然后用h1标签把它包围起来。

```java
private String parseMarkdownLine(String markdown_line) {
    String html_line = "";

    if (markdown_line.startsWith("#")){
        String h_text = markdown_line.split(" ")[1];
        html_line = "<h1>" + h_text + "</h1>";
    }

    html_line = html_line + "\n";
    return html_line;
}
```

此时运行一下，得到结果：
```
解析结果为：<h1>哈哈</h1>


错误！

```
有很多换行是因为“# 哈哈\nThis is a \*\*test\*\*. \n”中有2个“\n”，而解析时我们只处理了一级标题，其它的都还没处理，但虽然没处理，最后的`html_line = html_line + "\n";`却仍然会执行。

此时离目标已经近了一步。

接下来处理一下普通段落。

### 解析普通段落
这个应该比较简单了，普通段落不以任何特殊字符开头，所以不需要什么特别处理，直接给`if`加个`else`就行了：
```java
private String parseMarkdownLine(String markdown_line) {
    String html_line = "";

    if (markdown_line.startsWith("#")){
        String h_text = markdown_line.split(" ")[1];
        html_line = "<h1>" + h_text + "</h1>";
    } else {
        html_line = "<p>" + markdown_line + "</p>";
    }

    html_line = html_line + "\n";
    return html_line;
}
```

此时运行测试，结果为：
```
解析结果为：<h>哈哈</h>
<p>This is a **test**. </p>

错误！
```

离我们的目标还差一个加粗文本。

这时还是请出我们的正则表达式比较好办。

```java
private String parseMarkdownLine(String markdown_line) {
    String html_line = "";

    if (markdown_line.startsWith("#")){
        String h_text = markdown_line.split(" ")[1];
        html_line = "<h1>" + h_text + "</h1>";
    } else {
        html_line = "<p>" + markdown_line + "</p>";

        // 处理粗体文本
        html_line = html_line.replaceAll("\\*\\*(.*?)\\*\\*", "<b>$1</b>");
    }

    html_line = html_line + "\n";
    return html_line;
}
```

匹配`**test**`所使用的正则表达式应该是`\*\*(.*?)\*\*`。
`\*\*`好理解，本来是要找`**`，但是“\*”这个符号在正则表达式中有特殊意义，所以只能用反斜杠转义。
开头和结尾的两个星号理解完了，中间的`(.*?)`是个啥？
它表示以任意数量的字符（除去换行符）组成的字符串，其中`.`表示任意字符（除去换行符）、`*`表示重复任意多次、`?`表示非贪婪，即尽可能少地匹配字符。

此时再运行一下，发现测试通过了。
```
解析结果为：<h1>哈哈</h1>
<p>This is a <b>test</b>. </p>

成功！
```

## 四、换一个稍微复杂一点的例子
上面的例子确实太简单了，这次多加点行内元素，然后把标题的分级也加上，再加点图片和超链接吧。
```md
# 一级
## 二级
### ？级

这是*斜体*，这是`代码`，这是**粗体**。

![这是一张图片](https://pic.cnblogs.com/avatar/simple_avatar.gif)
[这是超链接](https://www.cnblogs.com/)
```

转为html应该为：
```html
<h1>一级</h1>
<h2>二级</h2>
<h3>？级</h3>

<p>这是<i>斜体</i>，这是<code>代码</code>，这是<b>粗体</b>。</p>

<p><img src="https://pic.cnblogs.com/avatar/simple_avatar.gif" alt="这是一张图片"></img></p>
<p><a href="https://www.cnblogs.com/" target="_blank" rel="noopener">这是超链接</a></p>
```

把markdown文本一换马上就出现了一个问题：上面的markdown文本含有空行，但在程序中仍会为空行生成一个`<p></p>`段落。
所以应该在`parseMarkdownLine`的if-else中添加一下空行判断：
```java
if (markdown_line.startsWith("#")){
    // ...
} else if ("" != markdown_line){  // 原来这里没有判断
    html_line = "<p>" + markdown_line + "</p>";
    // 处理粗体文本
    html_line = html_line.replaceAll("\\*\\*(.*?)\\*\\*", "<b>$1</b>");
    // 处理斜体文本
    html_line = html_line.replaceAll("\\*(.*?)\\*", "<i>$1</i>");
}

```

修改之后再运行测试：
```
解析结果为：<h1>一级</h1>
<h1>二级</h1>
<h1>？级</h1>

<p>这是<i>斜体</i>，这是`代码`，这是<b>粗体</b>。</p>

<p>![这是一张图片](https://pic.cnblogs.com/avatar/simple_avatar.gif)</p>
<p>[这是超链接](https://www.cnblogs.com/)</p>

错误！
```

这个结果和预期的就比较符合了，不过还是有多余的空行，这个如果想去掉的话，也可以给`parseMarkdownLine`方法最后的`html_line = html_line + "\n";`加个判断。

### 多级标题
<!-- 既然已经用了正则表达式了，那多级标题的效果也用正则表达式实现吧。
`(#+)\s+(.+)`是捕获标题行的正则表达式。
`(#+)`匹配一个或多个“#”号，`+`号表示一个或多个；
`\s+`表示一个或多个空白字符（空格、制表符、换行符）；
`(.+)`表示一个或多个任意字符。
 -->
在`parseMarkdownLine`中的`if (markdown_line.startsWith("#"))`已经能够获得以“#”开头的文本了。

接着我想可以用Java String类自带的`split`来分割“#”号和标题文本。
让我们看个例子：
```java
String s1 = "## Title";  
String[] s2 = s1.split("\s");  // ["##", "Title"]
```
这样我们就成功把标题元素的级别和标题文本分开了，只要统计一下有多少个“#”号就能知道是几级标题了。
> 这里不进行语法判断，就是如果有人写了“#323 Title”这样的语法，那我也只能拿它当4级标题了（摊手）。


```java
private String parseMarkdownLine(String markdown_line) {
    String html_line = "";
    if(markdown_line.startsWith("#")){
        String[] tmp = markdown_line.split("\s");
        int title_level = tmp[0].length();
        String title_content = tmp[1];
        markdown_line = markdown_line + "<h" + title_level + ">" + title_content + "</h" + title_level + ">";
    } else if (!"".equals(markdown_line)){
        html_line = "<p>" + markdown_line + "</p>";
        // 处理粗体文本
        html_line = html_line.replaceAll("\\*\\*(.*?)\\*\\*", "<b>$1</b>");
        // 处理斜体文本
        html_line = html_line.replaceAll("\\*(.*?)\\*", "<i>$1</i>");
    }
    html_line = html_line + "\n";
    return html_line;
}
```

运行一下：
```
解析结果为：<h1>一级</h1>
<h2>二级</h2>
<h3>？级</h3>

<p>这是<i>斜体</i>，这是`代码`，这是<b>粗体</b>。</p>

<p>![这是一张图片](https://pic.cnblogs.com/avatar/simple_avatar.gif)</p>
<p>[这是超链接](https://www.cnblogs.com/)</p>

错误！
```
处理多级标题成功！

### 图片和超链接
照旧使用我们的正则表达式吧。
```java
String markdownText = "[示例链接](https://example.com/)。这是一个![示例图片](https://pic.cnblogs.com/avatar/simple_avatar.gif)";
String result = markdownText.replaceAll("!\\[(.*?)\\]\\((.*?)\\)", "<img src=\"$2\" alt=\"$1\"></img>")  // 处理图片
                            .replaceAll("\\[(.*?)\\]\\((.*?)\\)", "<a href=\"$2\" target=\"_blank\" rel=\"noopener\">$1</a>");  // 处理超链接
```
也是突然才意识到这个replaceAll方法是一种函数式编程的思维——我可以一直点下去。

要注意的是，图片和超链接的md格式很像，图片比超链接多了个感叹号，所以要先处理图片。否则所有图片也会被当作超链接处理了。

### 行内代码
思路和粗体、斜体是一样的，多加一个replaceAll而已。

最后我们的解析器将长这个样子：
```java
public class MarkdownParser {
    // ...

    public String parseMarkdown(String markdown_text) {  // 解析md文本
        String html_text = "";  // 最终要返回的html文本
        for (String markdown_line : markdown_text.split("\n")){  // 将md文本分行，每次单独处理一行
            // 解析一行md文本
            String html_line = parseMarkdownLine(markdown_line);
            html_text = html_text + html_line;
        }
        return html_text;
    }

    private String parseMarkdownLine(String markdown_line) {
        String html_line = "";
        if(markdown_line.startsWith("#")){  // 处理标题
            String[] tmp = markdown_line.split("\s");
            int title_level = tmp[0].length();
            String title_content = tmp[1];
            html_line = html_line + "<h" + title_level + ">" + title_content + "</h" + title_level + ">";
        } else if (!"".equals(markdown_line)){
            
            html_line = markdown_line
                    .replaceAll("\\*\\*(.*?)\\*\\*", "<b>$1</b>")  //粗体
                    .replaceAll("\\*(.*?)\\*", "<i>$1</i>")  // 斜体
                    .replaceAll("`(.*?)`", "<code>$1</code>")  // 行内代码
                    .replaceAll("!\\[(.*?)\\]\\((.*?)\\)", "<img src=\"$2\" alt=\"$1\"></img>")  // 图片
                    .replaceAll("\\[(.*?)\\]\\((.*?)\\)", "<a href=\"$2\" target=\"_blank\" rel=\"noopener\">$1</a>");  // 超链接

            html_line = "<p>" + html_line + "</p>";
        }
        html_line = html_line + "\n";
        return html_line;
    }
}

```
运行一下，结果和我们期待的相同
```
解析结果为：<h1>一级</h1>
<h2>二级</h2>
<h3>？级</h3>

<p>这是<i>斜体</i>，这是<code>代码</code>，这是<b>粗体</b>。</p>

<p><img src="https://pic.cnblogs.com/avatar/simple_avatar.gif" alt="这是一张图片"></img></p>
<p><a href="https://www.cnblogs.com/" target="_blank" rel="noopener">这是超链接</a></p>

成功！
```

## 五、引用块、代码块
前面处理的都是行内元素，比较麻烦的就是引用块和代码块了。
因为不是行内元素，引用块和代码块显然不能放在`parseMarkdownLine`中实现了。
先试着将它放在`parseMarkdown`方法中实现。

首先从引用块开始吧！

### 引用块的实现
引用块感觉应该容易处理一些，只需要在遇到“> ”时加一个`<blockquote>`标签，然后在遇到两个连续的换行时加上`</blockquote>`即可。

试了一下，可以通过在parseMarkdown方法中添加一个
```java
public String parseMarkdown(String markdown_text) {  // 解析md文本
    String html_text = "";  // 最终要返回的html文本
    int ref_flag = 0;  // 整个标志，记录是否出现“> ”符号。大于1表示有引用嵌套
    for (String markdown_line : markdown_text.split("\n")){
        if (markdown_line.startsWith("> ")) {  // 若以“> ”开头，则ref_flag+1，同时给html加上<block>标签
            ref_flag = 1;
            html_text = html_text + "<blockquote>\n";
            markdown_line = markdown_line.substring(2);  // 加完<block>标签之后自然要把“> ”删掉了  
        }
        if (markdown_line.equals("") && ref_flag == 1) {  // 连续两个换行符是引用块结束的标志，因为md文本以换行符为界被分割开了，所以两个换行符之间应该是一个""字符
            ref_flag = 0;
            html_text = html_text + "</blockquote>\n";
            continue;
        }
        String html_line = parseMarkdownLine(markdown_line);
        html_text = html_text + html_line;

    }
    if (ref_flag == 1){  // 测试过程中发现，如果引用块的借书标志（两个换行符）在md文本的文末的话，最后一个""字符是不会出现在上面的for循环中的，只好修一下这个bug
        ref_flag = 0;
        html_text = html_text + "</blockquote>\n";
    }
    return html_text;
}
```
> 本来是要实现引用嵌套的，但发现还是挺麻烦的，放弃了。

### 代码块的实现
代码块的原理差不多，而且代码块不会有什么嵌套，代码块中的代码也不用经过任何解析，实际上是易于引用实现的（如果不管语法高亮这种东西的话）。
```java
public String parseMarkdown(String markdown_text) {  // 解析md文本
    String html_text = "";  // 最终要返回的html文本
    int ref_flag = 0;
    int code_flag = 0;
    for (String markdown_line : markdown_text.split("\n")){
        if (markdown_line.startsWith("> ")) {
            ref_flag = 1;
            html_text = html_text + "<blockquote>\n";
            markdown_line = markdown_line.substring(2);
        }
        if (markdown_line.equals("") && ref_flag == 1) {
            ref_flag = 0;
            html_text = html_text + "</blockquote>\n";
            continue;
        }
        if (markdown_line.startsWith("```")){  // 若以"```"开头，则看一下标志，标志为0说明这个```是代码块的开始，于是给html加个<code>；若标志为1说明这个```是代码块的结束，于是给html加个</code>。
            if(code_flag == 0){
                html_text = html_text + "<code>\n";
                code_flag = 1;                
            }else{
                html_text = html_text + "</code>\n";       
                code_flag = 0;     
            }
            continue;
        }
        if (code_flag == 1){
            html_text = html_text + markdown_line + "\n";
            continue;
        }
        String html_line = parseMarkdownLine(markdown_line);
        html_text = html_text + html_line;

    }
    if (ref_flag == 1){
        ref_flag = 0;
        html_text = html_text + "</blockquote>";
    }
    return html_text;
}
```

## 六、重构——责任链模式
这个简单的markdown解析器基本上就写好了。
但是可以看到这个代码的可读性很差，而且也没有用上设计模式。重构势在必行！

### 引用
每行markdown的处理方式需要根据开头的不同而不同，而处理之间又需要先后顺序，还可能需要根据具体情况有多种处理，感觉挺适合责任链模式的，那么就开干吧。

首先要编写一个处理markdown行的公共接口：
```java
public interface MarkdownLineHandler {
    void setNextHandler(MarkdownLineHandler nextHandler);  // 设置下一个处理者
    String handle(String markdown_line);  // 处理方法
}
```

从我们之前的程序看，第一个处理者应该是处理“> ”的引用处理者：
```java
package entity;

import java.util.Objects;

public class ReferenceHandler implements MarkdownLineHandler{
    private MarkdownLineHandler nextHandler;
    private int ref_flag = 0;
    @Override
    public void setNextHandler(MarkdownLineHandler nextHandler) {
        this.nextHandler = nextHandler;
    }

    @Override
    public String handle(String markdown_line) {
        Objects.requireNonNull(this.nextHandler);  // 保证一下确实有下一个处理者
        String html_text = "";
        if (markdown_line.startsWith("> ")  && ref_flag == 0) {  // 若以“> ”开头，则表示引用的开始
            ref_flag = 1;
            html_text = html_text + "<blockquote>\n";
            markdown_line = markdown_line.substring(2);
        } else if (markdown_line.equals("") && ref_flag == 1) {  // 若以“”开头，则表示引用的结束
            ref_flag = 0;
            html_text = html_text + "</blockquote>\n";
            return html_text;
        }
        return html_text + nextHandler.handle(markdown_line);
    }
}
```

到这里应该得先进行一下测试了，还不知道写得对不对呢。
先再写一个实现了`MarkdownLineHandler`的测试类，直接返回参数`mardown_line`本身，以便测试。
```java
public class TestHandler implements MarkdownLineHandler{
    private MarkdownLineHandler nextHandler;
    @Override
    public void setNextHandler(MarkdownLineHandler nextHandler) {
        this.nextHandler = nextHandler;
    }

    @Override
    public String handle(String markdown_line) {
        return markdown_line;
    }
}
```

再写个Main方法测试一下：
```java
public static void main(String[] args) {
    // 要处理的 Markdown 文本
    String markdown_text = "> 这是一个引用块的内容\n\nhah";

    // 设置一下责任链
    ReferenceHandler referenceHandler = new ReferenceHandler();
    TestHandler testHandler = new TestHandler();
    referenceHandler.setNextHandler(testHandler);

    String res = "";  // 存放结果

    for (String markdown_line: markdown_text.split("\n")){
        res = res + referenceHandler.handle(markdown_line);
    }
    System.out.println(res);

}
```

结果为：
```
<blockquote>
这是一个引用块的内容</blockquote>
hah
```
看着结果还是不错的。

接下来要加上代码块的处理了。

### 代码块
按照前面的思路直接上代码吧：
```java
public class CodeBlockHandler implements MarkdownLineHandler{
    // ... 

    @Override
    public String handle(String markdown_line) {
        Objects.requireNonNull(this.nextHandler);  // 保证一下确实有下一个处理者
        String html_text = "";
        if (markdown_line.startsWith("```")  ) {  // 若以“```”开头，则表示引用的开始
            if (code_flag == 0){
                code_flag = 1;
                html_text = html_text + "<code>\n";
            } else if (code_flag == 1){
                code_flag = 0;
                html_text = html_text + "\n</code>\n";
            }
            return html_text;
        } else if ( code_flag == 1) {  // 若code_flag == 1，则表示此行的内容属于代码块，直接返回
            return markdown_line;
        } else {  // 如果以上情况都不满足，那么说明是一个别的类型的md文本，传给下一个处理器处理。
            return nextHandler.handle(markdown_line);
        }
    }
}
```

再编写一个测试，包含单独的引用、单独的代码块、引用中嵌套代码块
```java
public static void main(String[] args) {
        // 要处理的 Markdown 文本
        String markdown_text = "> 这是一个引用块的内容\n" +
                "\n" +
                "hah\n" +
                "```\n" +
                "print(\"beng\");\n" +
                "```\n" +
                "\n" +
                "> ```\n" +
                "this is code block\n" +
                "```\n" +
                "\n" +
                "heihei"
                ;

        // 设置一下责任链
        ReferenceHandler referenceHandler = new ReferenceHandler();
        CodeBlockHandler codeBlockHandler = new CodeBlockHandler();
        TestHandler testHandler = new TestHandler();
        referenceHandler.setNextHandler(codeBlockHandler);
        codeBlockHandler.setNextHandler(testHandler);

        String res = "";  // 存放结果

        for (String markdown_line: markdown_text.split("\n")){
            res = res + referenceHandler.handle(markdown_line);
        }
        System.out.println(res);

    }
```
结果也还可以：
```
<blockquote>
这是一个引用块的内容
</blockquote>
hah
<code>
print("fuckyou");
</code>

<blockquote>
<code>
this is code block
</code>
</blockquote>
heihei
```

### 标题
不说了，直接上代码
```java
public class TitleHandler implements MarkdownLineHandler{
    // ...
    @Override
    public String handle(String markdown_line) {
        Objects.requireNonNull(this.nextHandler);  // 保证一下确实有下一个处理者
        String html_text = "";

        int titleLevel = 0;
        if (markdown_line.startsWith("# ")) {  // 若以“# ”开头，则表示一级标题
            titleLevel = 1;
        } else if (markdown_line.startsWith("## ")) {
            titleLevel = 2;
        } else if (markdown_line.startsWith("### ")) {
            titleLevel = 3;
        } else if (markdown_line.startsWith("#### ")) {
            titleLevel = 4;
        } else if (markdown_line.startsWith("##### ")) {
            titleLevel = 5;
        }

        // 标题级别为1的话，md文本就是“# title1”，从字母“t“开始接着处理，就是从”# title1“往后移动 1 + 1 个位置开始处理。
        // 标题级别为2的话，md文本就是“## title2”，从字母“t“开始接着处理，就是从”## title2“往后移动 2 + 1 个位置开始处理。
        // 标题级别为3的话，md文本就是“### title3”，从字母“t“开始接着处理，就是从”### title3“往后移动 3 + 1 个位置开始处理。
        // 所以归纳一下是从 titleLevel + 1 处 开始把md文本丢给下一个处理者处理
        if ( titleLevel > 0){
            markdown_line = markdown_line.substring(titleLevel + 1);
            return "<h" + titleLevel + ">" + markdown_line + "</h" + titleLevel + ">\n";
        } else {
            return nextHandler.handle(markdown_line);
        }
    }
}
```
这个`titleLevel`的取值判断方式，看起来很蠢，实际上确实也挺蠢的，但我目前没想到什么更好的办法。
> 后来问了一下ChatGPT，把那一串if-else换成了
```java
for (int i = 1; i <= 6; i++) {
    String prefix = "#".repeat(i) + " ";
    if (markdown_line.startsWith(prefix)) {
        titleLevel = i;
        break;
    }
}
```

测试一下
```java
public static void main(String[] args) {
    // 要处理的 Markdown 文本
    String markdown_text =
            "heihei\n" +
            "### This is title\n" +
            "> # title 1\n" +
            "\n" +
            "end\n" +
            "```\n" +
            "## hahha\n" +
            "```\n"
            ;

    // 设置一下责任链
    ReferenceHandler referenceHandler = new ReferenceHandler();
    CodeBlockHandler codeBlockHandler = new CodeBlockHandler();
    TestHandler testHandler = new TestHandler();
    TitleHandler titleHandler = new TitleHandler();

    referenceHandler.setNextHandler(codeBlockHandler);
    codeBlockHandler.setNextHandler(titleHandler);
    titleHandler.setNextHandler(testHandler);

    String res = "";  // 存放结果

    for (String markdown_line: markdown_text.split("\n")){
        res = res + referenceHandler.handle(markdown_line);
    }
    System.out.println(res);

}
```

```
heihei
<h3>This is title
</h3>
<blockquote>
<h1>title 1
</h1>
</blockquote>
end
<code>
## hahha
</code>

```

结果看着还不错，我也是到了这一步才知道其实引用里是可以有标题的。

### 行内元素
终于到最后的行内元素了，完成了这个基本就完成了重构了。
```java

```

### 最后的测试
搞一个全面一点的测试用例看看
```
# 标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题

> `引用中的行内代码块`
**引用中加粗**
*引用中斜体*
**引用中加粗2**
*引用中斜体*
![引用中图片链接](https://i.cnblogs.com/assets/adminlogo.png)
[引用中超链接](https://cnblogs.com)
引用正文

\```
这是代码块测试
### 代码中标题
`代码块中的行内代码块`
**代码块中加粗**
*代码块中斜体*
**代码块中加粗2**
*代码块中斜体*
![代码块中图片链接](https://i.cnblogs.com/assets/adminlogo.png)
[代码块中超链接](https://cnblogs.com)
代码：
print("你好")
\```
```

测试代码：
```java
public static void main(String[] args) {
    // 要处理的 Markdown 文本
    String markdown_text = "# 标题\n" +
            "## 二级标题\n" +
            "### 三级标题\n" +
            "#### 四级标题\n" +
            "##### 五级标题\n" +
            "\n" +
            "> `引用中的行内代码块`\n" +
            "**引用中加粗**\n" +
            "*引用中斜体*\n" +
            "**引用中加粗2**\n" +
            "*引用中斜体*\n" +
            "![引用中图片链接](https://i.cnblogs.com/assets/adminlogo.png)\n" +
            "[引用中超链接](https://cnblogs.com)\n" +
            "引用正文\n" +
            "\n" +
            "```\n" +
            "这是代码块测试\n" +
            "### 代码中标题\n" +
            "`代码块中的行内代码块`\n" +
            "**代码块中加粗**\n" +
            "*代码块中斜体*\n" +
            "**代码块中加粗2**\n" +
            "*代码块中斜体*\n" +
            "![代码块中图片链接](https://i.cnblogs.com/assets/adminlogo.png)\n" +
            "[代码块中超链接](https://cnblogs.com)\n" +
            "代码：\n" +
            "print(\"你好\")\n" +
            "```"
            ;

    // 设置一下责任链
    ReferenceHandler referenceHandler = new ReferenceHandler();
    CodeBlockHandler codeBlockHandler = new CodeBlockHandler();
    InlineElementHandler inlineElementHandler = new InlineElementHandler();
    TitleHandler titleHandler = new TitleHandler();

    referenceHandler.setNextHandler(codeBlockHandler);
    codeBlockHandler.setNextHandler(titleHandler);
    titleHandler.setNextHandler(inlineElementHandler);

    String res = "";  // 存放结果

    for (String markdown_line: markdown_text.split("\n")){
        res = res + referenceHandler.handle(markdown_line);
    }
    System.out.println(res);

}
```
结果为：
```
<h1>标题</h1>
<h2>二级标题</h2>
<h3>三级标题</h3>
<h4>四级标题</h4>
<h5>五级标题</h5>
<blockquote>
<p><code>引用中的行内代码块</code></p>
<p><b>引用中加粗</b></p>
<p><i>引用中斜体</i></p>
<p><b>引用中加粗2</b></p>
<p><i>引用中斜体</i></p>
<p><img src="https://i.cnblogs.com/assets/adminlogo.png" alt="引用中图片链接"></img></p>
<p><a href="https://cnblogs.com" target="_blank" rel="noopener">引用中超链接</a></p>
<p>引用正文</p>
</blockquote>
<code>
这是代码块测试
### 代码中标题
`代码块中的行内代码块`
**代码块中加粗**
*代码块中斜体*
**代码块中加粗2**
*代码块中斜体*
![代码块中图片链接](https://i.cnblogs.com/assets/adminlogo.png)
[代码块中超链接](https://cnblogs.com)
代码：
print("你好")
</code>
```
看着基本达到想要的效果了。

接下来就可以把责任链搬进`MarkdownParser`类里了。

```java
public class MarkdownParser {
    private final static MarkdownParser INSTANCE = new MarkdownParser();  // 将类实例定义为类变量
    private MarkdownParser() {}  // 只允许类中调用，防止外部调用
    public static MarkdownParser getInstance() {  // 获取全局唯一的类实例
        return INSTANCE;
    }

    public String parseMarkdown(String markdown_text) {  // 解析md文本
        ReferenceHandler referenceHandler = new ReferenceHandler();
        CodeBlockHandler codeBlockHandler = new CodeBlockHandler();
        InlineElementHandler inlineElementHandler = new InlineElementHandler();
        TitleHandler titleHandler = new TitleHandler();
        // 设置责任链
        referenceHandler.setNextHandler(codeBlockHandler);
        codeBlockHandler.setNextHandler(titleHandler);
        titleHandler.setNextHandler(inlineElementHandler);

        String html_text = "";  // 声明一下存放返回结果的字符串

        for (String markdown_line : markdown_text.split("\n")){  // 每次处理一行md文本
            html_text = html_text + referenceHandler.handle(markdown_line);
        }

        return html_text;
    }
}

```

## 七、从解析markdown字符串到解析md文件
其实就是把程序变成命令行程序。
首先肯定要知道怎么读取文件了，因为这个markdown解析器是一行一行解析的，所以先看看java怎么一行一行地读取文本文件吧。

### 解析责任链结合文件读写
```java
try (BufferedReader reader = new BufferedReader(new FileReader("example.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

再看看怎么按行写入文件：
```java
String filePath = "path/to/your/file.txt";
try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath))) {
    // 逐行写入内容
    writer.write("第一行");
    writer.newLine(); // 换行
    writer.write("第二行");
    writer.newLine(); // 换行
    writer.write("第三行");
    
    // 可以继续写入更多行...

    System.out.println("文件写入成功！");
} catch (IOException e) {
    System.out.println("写入文件时出现错误：" + e.getMessage());
}
```

试着把读入写出结合到一起：
```java
String sourceFilePath = "src/test.md";
String targetFilePath = "src/file.txt";

try (BufferedReader reader = new BufferedReader(new FileReader(sourceFilePath));
     BufferedWriter writer = new BufferedWriter(new FileWriter(targetFilePath))) {
    String markdownLine;
    while ((markdownLine = reader.readLine()) != null) {
        writer.write(markdownLine);
        writer.newLine(); // 换行
    }

    System.out.println("文件内容已成功复制到目标文件！");
} catch (IOException e) {
    System.out.println("文件操作时出现错误：" + e.getMessage());
}
```

在`while`循环中加一条解析markdownLine的指令就行了，不过在这之前要先把责任链搭好。

最终形成的main函数是这样的：
```java
public static void main(String[] args) {
    ReferenceHandler referenceHandler = new ReferenceHandler();
    CodeBlockHandler codeBlockHandler = new CodeBlockHandler();
    InlineElementHandler inlineElementHandler = new InlineElementHandler();
    TitleHandler titleHandler = new TitleHandler();
    // 设置责任链
    referenceHandler.setNextHandler(codeBlockHandler);
    codeBlockHandler.setNextHandler(titleHandler);
    titleHandler.setNextHandler(inlineElementHandler);

    String htmlText = "";  // 声明一下存放返回结果的字符串
    String markdownLine;

    String sourceFilePath = "src/test.md";
    String targetFilePath = "src/file.html";

    try (BufferedReader reader = new BufferedReader(new FileReader(sourceFilePath));
         BufferedWriter writer = new BufferedWriter(new FileWriter(targetFilePath))) {
        while ((markdownLine = reader.readLine()) != null) {
            htmlText = referenceHandler.handle(markdownLine);
            writer.write(htmlText);
        }

        System.out.println("解析成功！");
    } catch (IOException e) {
        System.err.println("文件操作时出现错误：" + e.getMessage());
    }
}
```
暂时没有用上命令行参数，还不知道IDEA怎么用命令行参数。javac的用法也忘了，不过不要紧，先把这个东西写好，后面再用一下应该十分简单。

## 八、MarkdownParser的去留，让各个Handler继承单例模式的一次尝试
一个很尴尬的问题是，如果做成命令行程序，而且是以行为单位解析md文本的话，MarkdownParser这个类似乎已经没有存在的必要了。
> 可是没有它就少了一个设计模式，很亏。

所以想了一下，还是把它去掉吧，但是要把这个单例模式套到这些责任链的Handler上。

为了做到这一点，挽救单例模式，于是只能手搓一个Singleton父类：
```java
public class Singleton {
    private final static Singleton INSTANCE = new Singleton();  // 将类实例定义为类变量
    private Singleton() {}  // 只允许类中调用，防止外部调用
    public static Singleton getInstance() {  // 获取全局唯一的类实例
        return INSTANCE;
    }
}
```
但是让Handler继承这个类的时候出现了点问题
```java
public class CodeBlockHandler extends Singleton implements MarkdownLineHandler {
    // ...
}
```
报错信息是`There is no default constructor available in 'entity.Singleton'`，问了一下ChatGPT，说得是父类有手写的构造函数，子类在继承之后，就也需要自己手写构造函数了。

所以应该让子类调用一下父类的Sington方法，才能实现通过子类继承父类的单例模式。
但这里还要修改一下，Singleton的构造函数是`private`属性的，子类无法调用，所以应该改成`protected`。
```java
public class CodeBlockHandler extends Singleton implements MarkdownLineHandler {
    private CodeBlockHandler(){
        super();  // 调用父类的构造方法
    }
```

但是在用`CodeBlockHandler codeBlockHandler = CodeBlockHandler.getInstance();`获取CodeBlockHandler实例的时候又出问题了。
报错信息为`Incompatible types. Found: 'entity.Singleton', required: 'entity.CodeBlockHandler'`，意思是`getInstance()`返回的是Singleton类，但此赋值语句需要的是CodeBlockHandler。

所以需要手动强转一下：
```java
CodeBlockHandler codeBlockHandler = (CodeBlockHandler) CodeBlockHandler.getInstance();
```
然后一运行，失败了……`Exception in thread "main" java.lang.ClassCastException: class entity.Singleton cannot be cast to class entity.ReferenceHandler (entity.Singleton and entity.ReferenceHandler are in unnamed module of loader 'app')`，大概意思是强转失败，不能把Singleton对象强转为CodeBlockHandler对象。
我想得重新想想这个Singleton类要怎么搞了……


## 九、Singleton类的丢弃
上面尝试失败的原因，我想是在Singleton的`INSTANCE`变量处，在父类中就直接把`INSTANCE`给new出来了，子类又调用了父类的构造方法，所以其实子类的`INSTANCE`里存放的也是父类的对象，而不是子类自己的对象。
除了上面那种写法，单例模式还有一种写法是：
```java
public class Singleton {
    private static Singleton INSTANCE;  // 将类实例定义为类变量
    protected Singleton() {}  // 只允许类中调用，防止外部调用
    public static Singleton getInstance() {  // 获取全局唯一的类实例
        if (INSTANCE == null){
            INSTANCE = new Singleton();
        }
        return INSTANCE;
    }
}
```
区别在于，这种写法把Singeton的实例的创建推迟到了创建时，这样我们才有办法通过重写`getInstance`来实现子类对子类对象的创建。
既然`getInstance`都是要重写的，那么为什么不直接在Singleton中实现了呢？
如果这么做，那Single类就可以写成抽象类了。

想得很美好，但实际操作时问题又出现了：
在写下这几行代码之后，又报错了
```java
public abstract class Singleton {
    private static Singleton INSTANCE;  // 将类实例定义为类变量
    public abstract static Singleton getInstance();
}
```

报错信息是：`Illegal combination of modifiers: 'abstract' and 'static'`，也就是说，静态函数和抽象函数只能取其一。

算了算了，不搞什么继承了，太麻烦了，本来以为通过继承能不用在每个Handler里都加那些同样的代码，现在看来还是我太天真了。

## 十、把每个Handler都写成单例模式
很无聊，cv工程，不多说了。

## 十一、命令行程序
先把程序的目录结构调整一下吧，不用IDEA了，直接用终端来操作一下。
<!-- 想得很美好，但是遇到了个问题：之前的1级标题是通过markdown文本是否以“#”开头来判断的，现在换成正则表达式，好像没法直接使用正则表达式来完成类似的判断啊。
> 或许有，但不想那么多了。

想了想，其实这个判断应该也没有必要存在，直接把markdown中出现的特殊标记全部用html标签来处理不就行了，还判断个啥。 -->


<!-- 本来可以把正则表达时`parseMarkdownLine`中的`if (markdown_line.startsWith("#"))` -->