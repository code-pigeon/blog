# Verifying shim SBAT data failed: Security Policy Violation
首次编辑：2024/8/19/18:04
最后编辑：2024/8/19/18:10

## 起因
Windows+Ubuntu双系统用户，在windows进行更新之后可能会出现这样的问题。
![图片](https://img.lancdn.com/landian/2024/08/105433.png)

> 我就是昨天切回了Windows，今天就出现了这个问题。

## 解决方法
在开机之后进入BIOS，关闭Secure Boot即可。

不过听说这是个临时解决方法，详细参考[蓝点网：Windows 10/11和Linux双系统用户请勿安装最新更新 否则系统将无法启动](https://www.landiannews.com/archives/105433.html)。