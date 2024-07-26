# 【python笔记】虚拟环境
### 1. 虚拟环境的建立
```bash
python -m venv <虚拟环境名>
# 例如：
python -m venv my_venv
```
### 2. 虚拟环境的激活与去激活
#### 激活
cd 到虚拟环境文件夹下的Scripts，在终端执行activate
#### 去激活
cd 到虚拟环境文件夹下的Scripts，在终端执行deactivate.bat

### 3. 在虚拟环境中下载库
```bash
python -m pip install numpy
```
### 4. 查看当前库依赖
```bash
python -m pip list
```
### 5. 把库依赖记录到requirements.txt中
```bash
python -m pip freeze > requirements.txt
```
### 6. 将requirements.txt中的依赖安装到虚拟环境中
```bash
python -m pip install -r requirements.txt
```

