# 不用IDE开发Java
## 环境配置

## 编译/运行文件
```bash
# 编译Main.java，生成Main.class
javac Main.java

# 执行Main.class（注意，不用加后缀，否则报错）
java Main  
java Main hh arg2  # 执行Main并传入命令行参数"hh"和"arg2"


# 若项目文件下有多个java文件：
# Main.java  Human.java
# 且Main.java中调用了Human.java
# 则直接执行javac Main.java，Human.java也会被编译


# 在给定路径中寻找并执行.class文件
java -cp .;entity Main  # 表示在当前目录下和entity文件夹下寻找class文件并执行，其中分号;为路径分割符（Windows），linux下为冒号:

# 在给定路径中寻找并编译.java文件
javac -cp .;entity Main.java


# 编译java文件，并将其放置到指定路径中
javac -d /bin Main.java
```

## 查看字节码信息
```bash
javap -c Main  # 查看Main.class的字节码信息
```

## jar相关
```bash
# 打包为jar
jar cvf MyLib.jar Human.class Animal.class

# 执行引用了jar的Main.class
java -cp entity/MyLib.jar;. Main

# 编译引用了jar的Main.java
javac -cp entity/MyLib.jar;. Main.java
```

## package相关
```bash
# 若Main.java在项目文件夹下，但Main.java并纳入包example中
# 即在Main.java中有"package example"这行代码
# 则应当新建文件夹example，并将Main.java移动到该文件夹中
# 此时项目结构为
# .\
#  |- bin\
#  |- example\
#  |         \- Main.java
#  |
# （假设bin是我们想要放置Main.class的文件夹）
# 然后在当前文件夹下编译Main.java
javac -d bin example/Main.java
# 此时项目结构为
# .\
#  |- bin\
#  |     \ - Main.class
#  |- example\
#  |         \- Main.java
#  |
# 此时在当前文件夹下执行Main.class
java -cp bin example.Main  # 必须加上example.因为包是文件的一部分
```