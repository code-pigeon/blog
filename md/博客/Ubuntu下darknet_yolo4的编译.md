# Ubuntu下darknet yolo4的编译
首次编辑：24/5/17/23:16
最后编辑：24/5/18/12:47

## 参考链接
1. [YOLOv4-darknet installation and usage on your system (Windows & Linux)](https://techzizou.in/yolo-installation-on-windows-and-linux/#install_linux)
2. [Installing and Building Darknet](https://www.ccoderun.ca/programming/2019-08-18_Installing_and_building_Darknet/)
3. [官网](https://pjreddie.com/darknet/install/)

## 0 说明
此博客只记录darknet yolo4 + opencv的编译安装，不涉及cuda和cuDNN。

## 1 编译的源文件
darknet的github地址为[https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet)。

> 首先要明确darknet这个darknet的版本，建议点开仓库中的`cfg`文件夹，看看里面有没有以`yolov4`开头的文件，有的话才是yolo4版本。
之前第一次编译的时候很神奇地编译了yolo3版本，但明明github链接地址看起来是一样的，还是谨慎为妙。

### 1.1 克隆仓库
```bash
git clone https://github.com/AlexeyAB/darknet.git
```
建议后面这个仓库链接还是直接去GitHub上复制。

### 1.2 修改Makefile
克隆完仓库之后，进入darknet文件夹。里面有个叫`Makefile`的文件，用代码/文本编辑器打开它。
在Makefile文件的前几行中：
```makefile
GPU=0  # gpu加速，应该就是配合cuda toolkit的
CUDNN=0  # 这个应该也是cuda加速的 
CUDNN_HALF=0  # 同上
OPENCV=0  
AVX=0  # x86架构处理器指令集的一个扩展，用于提高并行计算的速度
OPENMP=0  # Open Multi-Processing，cpu加速
LIBSO=0  # 是否将darknet编译成静态库
ZED_CAMERA=0  # to enable ZED SDK 3.0 and above
ZED_CAMERA_v2_8=0  # to enable ZED SDK 2.X
```
> 如果没有这么多选项那么应该是克隆错版本了。

将`OPENCV = 0`改为`OPENCV = 1`，如果有cuda和cudnn的话就把前三行的值都改为1。其它的几个选项可以根据自己的电脑情况和需求自行更改。

一般操作到这里就改完了，但由于我的opencv是通过源码编译安装的，还需要改一点东西。

--- 

**如果opencv是源码编译的**
在Makefile文件中找到下面片段：
```makefile
ifeq ($(OPENCV), 1)
COMMON+= -DOPENCV
CFLAGS+= -DOPENCV
LDFLAGS+= `pkg-config --libs opencv4 2> /dev/null || pkg-config --libs opencv`
COMMON+= `pkg-config --cflags opencv4 2> /dev/null || pkg-config --cflags opencv`
endif
```
将`LDFLAGS+=`后面的值改为
```
-L/path/to/opencv/lib -lopencv_gapi -lopencv_highgui -lopencv_ml -lopencv_objdetect -lopencv_photo -lopencv_stitching -lopencv_video -lopencv_calib3d -lopencv_features2d -lopencv_dnn -lopencv_flann -lopencv_videoio -lopencv_imgcodecs -lopencv_imgproc -lopencv_core
```
其中`path/to/opencv/`是opencv的路径。

然后将`COMMON+=`后面的值改为
```
-I/path/to/opencv/include/opencv4
```

### 1.3 执行Make
打开终端，进入darknet文件夹，执行`make`。等待编译完成。

## 2 测试darknet
### 2.1 测试可执行文件
打开终端，在darknet文件夹下，执行`./darknet`，若输出`usage: ./darknet <function>`，则表示编译成功。

### 2.2 测试物体识别功能
首先为了测试，我们要先下载一下别人训练好的权重文件。打开终端，在darknet文件夹下，执行：
```bash
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights
```

#### 检测图片
接着检测一下cv小狗的图片
```bash
./darknet detector test cfg/coco.data cfg/yolov4.cfg yolov4.weights data/dog.jpg
```
正常情况下，将会弹出一个窗口，正是那张经典的cv小狗加自行车的检测图像。
![cv小狗](https://techzizou.in/wp-content/uploads/2021/05/y4a.png)

#### 检测视频
> 没有装cuda的情况下，检测视频可能会非常慢，展示检测结果的窗口可能会很久才弹出。

```bash
./darknet detector demo cfg/coco.data cfg/yolov4.cfg yolov4.weights <video file>
```
把`<video file>`替换成你的视频文件名。

或者也可以将检测的结果保存成一个视频：
```bash
./darknet detector demo cfg/coco.data cfg/yolov4.cfg yolov4.weights <video file> -out_filename <output_video file>
```

#### 电脑相机实时检测
> 没有装cuda的情况下，实时检测可能会非常慢，展示检测结果的窗口可能会很久才弹出，甚至根本就没法弹出这个窗口，只会显示进程失去响应。

```bash
./darknet detector demo cfg/coco.data cfg/yolov4.cfg yolov4.weights
```