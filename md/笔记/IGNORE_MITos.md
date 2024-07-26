## 第1章-操作系统接口（Operating system interfaces）
设计一个好的接口是困难的：“简单易用的接口” vs “强大复杂的接口功能”是一对主要矛盾。
解决这一矛盾的主要方式：设计可组合在一起以提供更广泛用途的少量机制。

### kernel
xv6系统中，每个进程（process）包含`instructions（指令）`、`data（数据）`和`stack（栈）`。（栈用于管理程序调用，其它两个比较简单）

kernel是一个特殊的程序，用于给进程process提供服务。

操作系统中可以有很多进程，但只有一个kernel。

进程如何使用kernel提供的服务？
1. 进程调用系统调用（system call）——一个操作系统接口（operating system interface）；
2. 系统调用进入kernel；
3. kernel进行服务，并返回（return）；

所以一个进程在此过程中，分别在用户空间（user space）->核心空间（kernel space）->用户空间中切换执行。

> kernel使用CPU提供的硬件保护机制（hardware protection mechanisms）来保证进程只会访问自己在用户空间中的内存空间。  
> kernel拥有提供这种硬件保护机制的硬件权限；而用户程序没有。  
> 当用户进程使用系统调用时，硬件会提高它的权限级别，并执行kernel中预置的函数（这句看不懂，后面章节应该会详细讲）。

### 1.1 进程和内存
**xv6进程**：
由
1. 指令、数据、栈
2. 每个进程的状态（只对kernel可见）

组成。

**xv6时间共享进程（xv6 time-shares processes）**：It transparently switches the available CPUs among the set of processes waiting to execute. （看不懂照抄）

当一个进程不执行时，xv6保存进程的寄存器内容，以便下次运行时使用。每个进程在kernel中都有一个PID。

#### 子进程和fork
进程通过使用fork系统调用来创建子进程。fork会分配一块和父进程一模一样（包括指令和数据）的新内存空间给子进程，然后返回子进程的PID给父进程，返回0给子进程。

例子（可以看我做的演示视频[【操作系统——MIT 6.828 xv6讲义视频演示】创建子进程——fork系统调用是怎么工作的？](https://www.bilibili.com/video/BV1qC4y1E7Fe?t=1.8)）：
```c
// 如上所言，父进程和子进程都会执行int pid = fork()这条语句
// 但父进程得到的是子进程的PID
// 而子进程执行此句时得到的是0
int pid = fork();

if(pid > 0){
	printf("parent: child=%d\n", pid);
	pid = wait((int *) 0);
	// wait系统调用返回运行结束的子进程的PID
	// 并且将子进程的退出状态（就是子进程exit(0)时带的那个0）赋值给传入的指针（就是wait的参数——wait(int *status)里的这个int*）指向的变量
	// 如果不需要获取子进程的状态，wait中可以传入0地址（就像本例这样）
	// 如果没有子进程退出，父进程会一直卡在wait这里
	// 如果没有子进程存在，wait会马上返回-1

	printf("child %d is done\n", pid);
} else if(pid == 0){
	printf("child: exiting\n");
	exit(0);  
	// exit让使用exit的进程结束，并释放相应的资源（如内存、打开的文件等）。
	// exit接收一个整型状态参数，通常以0表示成功，1表示失败。
} else {
	printf("fork error\n");
}
```

**exec系统调用**：
若进程使用exec系统调用，该进程的内存会被替换为从文件系统加载的（可执行）文件的内存映像（Memory Image）（这句话可以简单理解为“把调用exec的进程所使用的内存拿去给可执行文件用了”），这个（可执行）文件必须拥有特别的格式——此格式指出指令、数据、指令入口在文件的什么位置（例如，xv6使用ELF格式——下一章会详细讨论）。通常这个（可执行）文件是已编译的文件。
当exec执行成功，PC不会直接回到调用exec的进程，而是指向（可执行）文件的指令入口（这个指令入口的位置存储在ELF header中），从而执行这个（可执行）文件。
exec接收两个参数：1）可执行文件；2）string类型的数组（其实就是命令行参数）（很多程序忽略数组的第一个元素——通常此元素表示要运行的程序的名字）；

例如：
```c
char *argv[3];
argv[0] = "echo";  // 如上所言，argv的第一个元素就是exec要调用的程序的名字：本例中为echo
argv[1] = "hello";
argv[2] = 0;
exec("/bin/echo", argv);
printf("exec error\n"); // 假如exec执行成功了，程序应当是不会执行到此句代码的。
```

xv6 shell也是用上面的方式代替用户运行程序。
（下面的xv6 shell源码摘抄自[user/sh.c](https://github.com/mit-pdos/xv6-riscv/blob/riscv//user/sh.c#L146)）
```c
int getcmd(char *buf, int nbuf)
{
  // 此处不向标准输出打印提示符，而向标准错误打印提示符，应该是为了不让提示符和程序的输出混在一起。
  write(2, "$ ", 2);  // 参数1：2指标准错误输出；参数2：要写入的字符；参数3：指写入2个字符；
  memset(buf, 0, nbuf);
  gets(buf, nbuf); // 将文件读入标准输入了，处理输入的部分在main程序的while循环里
  if(buf[0] == 0) // EOF
  	// EOF应该是接收到ctrl + z，即^Z才算EOF，直接回车应该就是正常换行
    return -1;
  return 0;
}

int main(void)
{
  static char buf[100];
  int fd;

  // Ensure that three file descriptors are open.
  while((fd = open("console", O_RDWR)) >= 0){
  	// 这里的open(char *file, int flags)是系统调用，返回文件描述符
  	// O_RDWR是fcntl.h头文件中定义的宏常量，表示以读写方式打开文件。
  	// 所以这个语句应该是打开console这个可执行文件
    if(fd >= 3){
      //fd为0、1、2分别代表标准输入、标准输出、标准错误，大于3则表示成功打开了其它文件
      close(fd);
      break;
    }
  }

  // Read and run input commands.
  while(getcmd(buf, sizeof(buf)) >= 0){
    if(buf[0] == 'c' && buf[1] == 'd' && buf[2] == ' '){
      // Chdir must be called by the parent, not the child.
      // 上面这句注释是给if判断注释的
      // 弄懂这句话的意思要先看一下这个if判断和下面的fork的顺序关系
      // 如果用户输入的是除了cd之外的指令，那么shell会开一个子shell进程，让子shell进程执行用户输入的命令
      // 如果用户输入的是cd，那么这句cd就不应该被子shell执行，而应该直接在当前shell中执行，然后等待用户下一轮输入

      buf[strlen(buf)-1] = 0;  // chop \n 
      // 因为每次输入是以回车结束的，也就是以\n结尾，此行的作用就是把输入的结尾\n去掉

      if(chdir(buf+3) < 0)  // chdir是一个系统调用，接收一个字符指针，指向的字符串是文件夹的路径
      	// chdir失败时返回-1（我猜的，按照习惯应该是-1）
        fprintf(2, "cannot cd %s\n", buf+3);
      continue;
    }
    if(fork1() == 0)  
    // 执行了fork之后，父shell开辟子shell进程，子shell和父shell完全一致，因此子shell也会执行到此句命令
	// 而因为父shell执行fork得到的子shell的PID，子shell执行fork得到的是0
	// 所以子shell中if判断成立，会执行下面的runcmd来执行用户输入
	// 而父shell中if判断不成立，会接着执行wait，等待子shell执行完毕
      runcmd(parsecmd(buf));  
      // 这个命令将解析用户输入并执行，runcmd会调用exec
      // 假如用户输入的是echo hello，runcmd嗲用exec成功后，PC将指向echo的入口指令，
      // 直到echo执行结束，PC才会返回到子shell的runcmd
    wait(0);
  }
  exit(0);
}
```
xv6隐式分配用户空间内存：如fork分配和父进程相同的子进程空间；exec分配足够的内存以容纳可执行文件。
若进程在运行时，又需要额外的空间（可能由于malloc的使用），可以使用sbrk(n)系统调用，sbrk(n)可以增加n给字节给调用sbrk的程序的数据内存，并返回新内存的位置。

### 1.2 I/O与文件描述符
文件描述符是一个短整型（small integer），用于表示进程可以读/写的kernel管理对象（kernel-managed object）。
进程可以通过打开文件、文件夹、设备、创建管道、复制已存在的文件描述符，来获取文件描述符。
文件描述符接口（file descriptor interface）将文件、管道、设备全部抽象为字节流（streams of bytes）。

xv6中，每个进程都拥有一个存有文件描述符的表（一下简称fd表）。（文件描述符从0开始，0、1、2永远被占用——见下文，打开新文件之后，总是使用最小的未被使用的整数作为文件描述符）
按照惯例，文件描述符为0表示标准输入（用于读取用户输入）；1为标准输出（用于输出正常信息）；2为标准错误输出（用于输出错误信息）。

**read和write系统调用**：通过文件描述符向打开的文件读取或写入字节信息。

read(fd, buf, n)从文件描述符为fd的文件（以下简称文件fd）读取至多n个字节数据，并将数据复制到buf中，返回读入的字节数。
文件描述符包含一个offset（当成一个变量或者指针看即可，我个人更愿意称它为“读写指针”或者“读写光标”，就像我们打开记事本的时候，有个光标，我们写入文本时，光标就会往后面移动），read从文件的开头往后偏移offset个字节的位置读取数据，假如读取了n个字节，那么offset就加n（下一次read时，将从新的offset的位置开始）。
若没有字节可读，read将返回0。

write(fd, buf, n)向文件fd写入n个来自buf中的字节，返回写入的字节数。
若写入少于n个字节数据，则意味着发生了错误。
和read一样，fd也包含一个offset。

例如（此程序实际上就是cat）：
（如果你没学过Linux，不知道cat，按照下面这个简化版cat的功能来看，就是读取fd（文件描述符）为0的文件的内容，然后将此内容写入fd为1的文件中）
```c
char buf[512];
int n;
for(;;){
	n = read(0, buf, sizeof buf);
	if(n == 0)
		break;
	if(n < 0){
		fprintf(2, "read error\n");
		exit(1);
	}
	if(write(1, buf, n) != n){
		fprintf(2, "write error\n");
		exit(1);
	}
}

```
> 如果学过Linux的同学可能会疑惑：cat不是用来打印文件内容的吗？怎么只能打印标准输入了？  
> 虽然看起来，cat只能从标准输入读数据，向标准输出写数据（因为我们按照惯例让标准输入的fd为0，标准输出为1），但假如我们偷偷把其它文件的fd改成0呢？  
> 这个方法便是——I/O重定向（先不做解释，记住这个名词即可）。

> 下面这段有点抽象，看不懂可以直接跳过，先看下面的例子。

#### I/O重定向的实现

文件描述符和fork接口使得I/O重定向（I/O redirection）很容易实现。fork复制父进程的fd表和内存，故子进程被开辟时就已经拥有父进程所打开的所有文件了。exec会替换掉调用exec的进程的内存（见“1.1 进程和内存 子进程和fork”下的“exec系统调用”），但保留了进程的fd表。
这样就使得shell能够用fork实现I/O重定向——在子进程中打开要被重定向的文件。

例（简化版的cat < input.txt命令执行程序）：
（“< input.txt”中，< 表示输入重定向，原来输入的内容从命令行用户输入读取，但现在输入的内容从input.txt读取）
```c
char *argv[2];
argv[0] = "cat";
argv[1] = 0;

// 调用fork时，shell会新建一个子shell，子shell拥有父shell相同的所有fd
// 但在子shell中我们可以修改fd表——这并不影响父shell的fd表
// 而且执行exec调用时，虽然进程的内存被替换了，但fd表仍然会得到保留
// 以上特点为实现重定向提供了可能（请看下面分析）
if(fork() == 0) {
	close(0);  // close系统调用接收一个fd作为参数，作用是释放该fd
	// 在这里，0本来是标准输入的文件描述符，但此时我们将它close了，则fd不再表示标准输入，而是一个置空的fd

	open("input.txt", O_RDONLY); // 上文中我们提过，open打开文件时，总是会优先使用最小的空闲（即没有被使用的）整数作为fd
	// 而上面的代码中，0这个fd已经被释放了，所以打开input.txt时，0这个fd就被分配给了input.txt
	// O_RDONLY表示以只读的方式打开

	exec("cat", argv);  // 此时再执行cat程序，cat程序还是从fd为0的文件中读入数据
	// 而fd为0的文件此时已经变成了input.txt，所以就成功实现了从input.txt中读取数据
}

```
#### 标准错误输出的重定向

fork在复制父进程的fd表的时，每个fd对应的offset也会被复制。
如：
```c
// 此程序将输出hello world\n
if(fork() == 0) {
	write(1, "hello ", 6);
	exit(0);
} else {
	wait(0);
	write(1, "world\n", 6);
}
```

**dup**系统调用：
通过已经存在的fd（称为fd0），创建一个新的fd（称为fd1)，fd1指向fd0所指向的文件（fd1拥有与fd0相同的offset）。
（如果听得迷糊，可以看我做的演示视频：[【操作系统——MIT 6.828 xv6讲义视频演示】dup系统调用是怎么工作的？](https://www.bilibili.com/video/BV1bu4y1b7Dn)）
```c
// 此程序也能输出hello world\n
fd = dup(1);
write(1, "hello ", 6);
write(fd, "world\n", 6);
```

除了以上两种情况，offset都不会被复制——即便是open了两个一样的文件。

xv6并不支持直接的标准错误重定向，但可以利用dup系统调用来实现。

```shell
# ls 后面跟文件名，若该文件存在，则打印文件名到终端（标准输出）；若不存在，则输出报错信息（标准错误输出）
# > 表示重定向，输出的内容将不再在终端显示，而是写入到名为tmp1的文件中。
# 一般情况下 > 只能重定向标准输出的内容
# 但后面加上 2>&1，将2号fd重定向到1号fd
# （原文的说法是，2>&1告诉shell 2号fd是1号fd的副本，但这个说法有点怪，我不太懂，可能是直接将2号fd指向了和1号fd指向的文件的意思）
ls existing-file non-existing-file > tmp1 2>&1
```

### 1.3 管道（Pipes）
管道是一个空间很小的kernel缓存区（kernel buffer），如其名之意，管道有两个端口，一端用于输出（读），一端用于输入（写）。从一端写入的数据可以从另一端被读取。

管道的这两个端口都有自己对应的fd，可以被进程所使用。

管道的特性使得不同进程之间能够相互交流。

```c
int p[2];  //用于存放管道端口的fd
char *argv[2];
argv[0] = "wc";
argv[1] = 0;
pipe(p);  // pipe系统调用创建一个管道，并把对应的读/写fd放入p[0]和p[1]中。
if(fork() == 0) {
	close(0);  // 释放了0这个fd
	dup(p[0]);  // 0这个fd空闲着，因此dup p[0]（即管道读端口的fd）后，0号fd就指向管道的读端口了。
	close(p[0]); 
	close(p[1]);
	exec("/bin/wc", argv);  // wc程序会从0号fd读取输入，因为0号fd已经指向管道的读端口了，所以会从管道读入内容
} else {
	close(p[0]);  // 父进程关闭管道读端口
	write(p[1], "hello world\n", 12);  // 并向写端口写入数据
	close(p[1]);
}

```

在上面的代码中，子进程在执行wc之前将管道写端释放（即close，或者说关闭)了——而且必须这么做。
这是因为：

read系统调用读取管道数据时，如果管道中没有数据，那么read会等待数据从管道写端被写入、或者等待所有指向管道写端的fd都被释放。
如果是后一种情况，read会返回0——就像读到了文件结尾一样。

所以如果没有将管道写道关闭，read系统调用将一直等待管道的写端输入数据。

在xv6 shell中，实现包含管道符（|）的命令的方法与上面的代码类似，比如grep fork sh.c | wc -l（原文中把含有管道符|的命令叫做流水线——pipelines）。
原理是：创建一个管道将“|”左边的部分命令的输出连接到“|”右边部分的输入，然后再创建两个子进程，一个运行左边的命令，一个运行右边的命令；接着等待两个命令都完成。
如果右边的命令又包含管道符，那么对右边的命令执行和以上相同的操作——这将产生一个树形结构，树的叶子节点表示命令，而非叶子节点则是等待左右孩子节点完成的进程。

例如（见[user/sh.c:101](https://github.com/mit-pdos/xv6-riscv/blob/riscv/user/sh.c#L169)）
```c
struct cmd
{
	int type;  // 标记命令行语句的类型
};

struct pipecmd
{
	int type;  // 标记命令行语句的类型
	struct cmd *left;  // 指向位于|左边的命令
	struct cmd *right;  // 指向位于|右边的命令
};

// 在命令行中输入的语句，最终都会用runcmd来执行
runcmd(struct cmd *cmd)
{
  int p[2];  // 存放管道fd
  struct pipecmd *pcmd;


  if(cmd == 0)
    exit(1);

  switch(cmd->type){
  default:
    // ...
  case EXEC:
    // ...
  case REDIR:
    // ...
  case LIST:
  	// ...
  case PIPE:
  	// 如果解析出的结果是含有管道符的语句，则会执行下列语句
    pcmd = (struct pipecmd*)cmd;
    if(pipe(p) < 0)
      panic("pipe");  // 错误处理
    if(fork1() == 0){  // 创建一个子进程，用于处理管道符|左边的语句
      close(1);  
      dup(p[1]);  // 关闭标准输出，使1号fd指向管道写端
      close(p[0]);
      close(p[1]);
      runcmd(pcmd->left);  // 执行|左边的语句
    }
    if(fork1() == 0){  // 创建另一个子进程，用于处理管道符|右边的语句
      close(0);
      dup(p[0]);  // 关闭标准输入，使0号fd指向管道写端
      close(p[0]);
      close(p[1]);
      runcmd(pcmd->right);  // 执行|右边的语句
    }
    close(p[0]);
    close(p[1]);
    wait(0);
    wait(0);
    break;

  case BACK:
    // ...
  }
  exit(0);
}

```

#### 管道vs重定向
`echo hello world | wc`这条语句也可以用`echo hello world > /tmp/xyz; wc </tmp/xyz`来实现。
但管道具有至少三个优点：
1. 重定向需要中间文件来暂存信息，但管道不需要；
2. 管道可以传输任意大小的数据，而用文件重定向则需要考虑空间大小。
3. 重定向只能先等第一条指令执行完才能继续执行第二条，但管道可以使它们并行运行。（不过我不是很清楚如果左边的命令没有执行完成，右边的程序怎么得到输入呢？）

### 1.4 文件系统File system
#### 与创建文件相关的系统调用
```c
mkdir("/dir");  // 新建文件夹
fd = open("/dir/file", O_CREATE|O_WRONLY);  
close(fd);
mknod("/console", 1, 1);  // 第二、三个参数分别是大设备数和小设备数——它们是kernel设备的ID
// 当进程打开设备文件，并对设备文件执行read或write系统调用时，kernel会对设备的读写进行特殊处理。
// 原文是（When a process later opens a device file, the kernel diverts read and write system calls to the kernel device implementation instead of passing them to the file system.）
```

#### 文件名与文件
（这段话就比较难翻译了）
A file’s name is distinct from the file itself; the same underlying file, called an inode, can have multiple names, called links. Each link consists of an entry in a directory; the entry contains a file name and a reference to an inode. An inode holds metadata about a file, including its type (file or directory or device), its length, the location of the file’s content on disk, and the number of links to
a file.

> 大体理解：一个文件可以有很多个链接，我们平时在操作系统上看到的文件名，其实就是个链接，它会链接到一个真正的文件上，而真正的文件都包含有一个inode，inode中有文件的metadata（其实就是文件的信息），包括文件类型、大小、位置以及此文件的链接数量。

`int fstat(int fd, struct stat *st)`系统调用可以通过fd获取文件的metadata。
其中`struct stat`类型定义在头文件`stat.h`（见[kernel/stat.h](https://github.com/mit-pdos/xv6-riscv/blob/riscv//kernel/stat.h)）中：
```c
#define T_DIR 1 // Directory
#define T_FILE 2 // File
#define T_DEVICE 3 // Device
struct stat {
	int dev; // File system’s disk device
	uint ino; // Inode number inode的唯一ID
	short type; // Type of file
	short nlink; // Number of links to file
	uint64 size; // Size of file in bytes
};
```

`int link(char *file1, char *file2)`系统调用为已经存在的file1创建一个新的文件名file2（link）。

例如：
```c
open("a", O_CREATE|O_WRONLY);
link("a", "b");  // 如此一来，对a的读写等价于对b的读写
```
在上面的例子中，我们可以用`fstat`来判断a和b是否是同一个文件（读取它们的ino）。

`int unlink(char *file)`移除一个文件名，只有当一个文件的nlink=0且没有fd指向此文件时，这个文件的inode和它占用的磁盘空间才会真正被释放。

若要在程序中创建一个不会被保存的匿名文件，有一种惯用的写法：
```c
fd = open("/tmp/xyz", O_CREATE|O_RDWR);
unlink("/tmp/xyz");
// 当fd被释放或程序退出之后，此文件就不存在了
```

> Unix提供用户层面的文件操作程序（如mkdir、ln、rm）以便用户扩展命令行接口。看似显然需要这么设计，但同时期的其它操作系统并不如此，它们常常将这些命令设计成shell内部的命令（而且把shell设计成kernel内部的程序）。
> 
> 但cd是个例外，因为我们需要在当前shell中切换文件路径，而不是在子shell中（用户层面命令的执行是在当前shell中新建子shell，并在子中执行完再退出回到当前shell中，如果把cd设计成用户层面的命令，那么切换路径的只会是子shell——而当前shell的路径却没有发生改变）。

1.5 现实世界Real world
（都是吹水）