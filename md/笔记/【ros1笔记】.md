# ros1笔记
## 先修事项
- ros的安装
- ros的包（package）和节点（node）的概念

## 第一个package
准备好项目文件夹：
```
catkin_ws/
    src/
```
进入到`catkin_ws/src`路径下，执行：
```bash
catkin_create_pkg my_package rospy roscpp std_msgs
```
其中，第一个参数`my_package`是自己创建的包名，后面的`rospy roscpp std_msgs`为包的依赖项。
此命令执行后，会在执行该命令的路径下生成`my_package`文件夹，该文件夹中有2个文件夹（`include`和`src`）、2个文件（`CMakeLists.txt`和`package.xml`）。
此时项目文件夹的内容如下：
```
catkin_ws/
    src/
        my_package/
            include/
            src/
            CMakeLists.txt
            package.xml
```
此时再返回到路径`catkin_ws`下，执行：
```bash
catkin_make
```
将会在`catkin_ws`路径下生成`build`和`devel`文件夹。
此时项目文件夹变为：
```
catkin_ws/
    build/
    devel/
        setup.bash
        ...
    src/
        my_package/
            include/
            src/
            CMakeLists.txt
            package.xml
```

## 一些准备工作
以我目前的认识来看，所有的ros包应该都会放在`catkin_ws`下了。
为了让我们自己创建的ros包能够随时被终端调用，我们需要在`~/.bashrc`中添加如下bash指令：
```bash
source /path/to/catkin_ws/devel/setup.bash
```
其中`/path/to/catkin_ws/devel/setup.bash`应替换为你的`catkin_ws/devel/setup.bash`所在的路径。

## hello world程序
虽然在之前我们创建了自己的包，但是这个包是个空包，没有任何内容，现在我们要在`my_package`这个包中添加我们的第一个程序。
首先要在`my_package/CMakeLists.txt`的文件末尾添加代码：
```cmake
add_executable(hello_node src/hello.cpp)
```
这行代码的作用是为我们的`my_package`包添加一个`hello_node`节点。
其中第一个参数`hello_node`是我们创建的节点名，第二个参数`src/hello.cpp`是节点名对应的源文件的路径。
接着再添加一行代码：
```cmake
target_link_libraries(hello_node
    ${catkin_LIBRARIES}
)
```
这行代码的作用是：让编译`hello_node`节点源文件时，链接库文件（这里对应的就是`catkin_LIBARARIES`所存储的值了，这个变量是catkin定义的，我们不去管它）。

然后在`my_package/src`路径下新建一个源文件，起名为`hello.cpp`。
写入代码：
```c++
int main(int argc, char const *argv[])
{
    ros::init(argc, argv, "hello_node");  // 初始化ros
    std::cout << "hello，ros" << std::endl;
    return 0;
}
```

这时候我们的hello world程序就已经准备好了，接着需要进行构建编译。
我们先进入到`catkin_ws`目录下，然后执行命令：
```bash
catkin_make
```
等待编译完成后，执行命令：
```bash
ros_run my_package hello_node
```
这时看到`hello, ros`输出则表示成功。
