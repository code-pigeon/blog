# Windows设置视觉风格（visual style）
首次编辑：2024/7/23/17:48
最后编辑：2024/7/24/9:36

## 引子
很多时候，无论使用什么语言什么库，似乎只要在Windows下写出来的桌面应用，外观都是奇丑无比：
![Windows默认的应用风格](https://www.codeproject.com/KB/vista/620045/win2000.png)

这是Windows控件的默认风格，老版的Windows程序窗口都长这副模样。但对于今天的审美来说这肯定是个灾难。Windows也明白这一点，所以在后来的版本中支持了不同风格的窗口控件，称之为视觉风格（visual style）。
> 但到后面的时候我才意识到其实Windows只提供了两种风格，要想设置其它的风格，就得自己动手了……

比如下面这张图片中的窗口便是win8风格的：
![win8风格窗口](https://learn.microsoft.com/en-us/windows/win32/controls/images/tb-win8.png)

所以程序员要如何为自己的程序切换稍微好看一点的视觉风格呢。

参考了微软文档[^1]，果不其然，依旧是只提供MSVC的解决方式，用别的编译器那就别玩了。
MSVC，也就是使用visual stdio的解决方法相当简单，可以直接参考微软文档。

这里主要讲用mingw gcc怎么设置这个风格。

## 方法
1. 第一步是要创建一个`.manifest`资源文件（其实是`.xml`文件），用于描述程序所要使用的视觉风格，文件内容摘自微软官网。
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="CompanyName.ProductName.YourApplication"
    type="win32"
/>
<description>Your application description here.</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="*"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
```
这里面重要的地方还是下面那个`<dependency>`中的`version=6.0.0.0`，就是它指定了好看一点的视觉风格，默认的那个风格的这个值好像是`5.0.0.0`。
还有一些地方是可以自定义的，比如`<description>Your application description here.</description>`这里的描述可以自己写，还有`name="CompanyName.ProductName.YourApplication"`，依次为公司名、产品名、应用名，都可以自定义。

我也是刚了解这个`.manifest`文件，我猜测它的作用就是告诉操作系统这个程序的一些信息吧（这个`.manifest`最后会合并到`.exe`文件中），比如`    processorArchitecture="*"`的作用是告诉操作系统，这个应用程序所支持的处理器架构有哪些。`*`表示支持所有架构，还可以填`X86`、`amd64`等。如果`.exe`通过这个`.manifest`文件指定了某个处理器架构，而恰好执行这个`.exe`的电脑又不是这个处理器架构的，那么操作系统应该不会允许启动这个`.exe`（我是这么猜的，具体实验有闲再做了）。

2. 接着需要创建一个`.rc`文件：
```rc
1 24 "example.manifest"
```
很重要的是这里前面两个数字是固定的！！！
第一个数字`1`代表资源的ID，**一定**要是1！！！否则后面视觉风格将无法生效。
第二个数字代表着资源的类型，`24`表示是`manifest`资源（理论上可以把`24`换成`RT_MANIFEST`——见[微软官网](https://learn.microsoft.com/en-us/windows/win32/menurc/resource-types)，但是改成`RT_MANIFEST`不知为啥就会失效）。
第三个字符串表示的就是刚刚创建的`.manifest`文件的文件名（随意起名）。

3. “编译”`.rc`文件：
在命令行下执行
```bash
windres example.rc -o example.o --use-temp-file
```
得到目标文件`example.o`。

4. 然后将`example.o`和你的代码文件或者目标文件一起编译链接：
```bash
gcc -o main.exe main.c example.o 
```
到这里一个带有新风格的Windows窗口应该就完成了。

5. 如果预期的效果没有出现，那么可以在源文件和链接上再加点东西：
```c
/* main.c */

#include <commctrl.h>  // 多包含一个头文件
#define _WIN32_WINNT 0x0600  // 再定义两个宏
#define _WIN32_IE 0x0900
// 其它宏定义...

// ...

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow)
{

	// ---- 加上下面的代码来保证正确的commctrl32被调用
    INITCOMMONCONTROLSEX icc;

    // Initialise common controls.
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_WIN95_CLASSES ;
    InitCommonControlsEx(&icc);

	// 主函数其它内容...
	// ...
}
```
这一部分内容在参考[^2][^3][^4]中均有提及，对于其中的含义和细节，感兴趣的可以去浏览一下。

## 参考
[^1]:微软官方，[Visual Styles](https://learn.microsoft.com/en-us/windows/win32/controls/themes-overview)
[^2]:codeproject文章，[Custom Controls in Win32 API: Visual Styles](https://www.codeproject.com/articles/620045/custom-controls-in-win-api-visual-styles)
[^3]:geekthis，[Visual Styles in Win32 API C GCC MinGW](https://geekthis.net/post/visual-styles-in-win32-api-c-gcc-mingw/)
[^4]:Transmission Zero，[Building Win32 GUI Applications with MinGW](https://www.transmissionzero.co.uk/computing/win32-apps-with-mingw/)
