# git笔记
**参考视频**：
[【GeekHour】一小时Git教程](https://www.bilibili.com/video/BV1HM411377j)
[【Git全套教程】轻松搞笑 快速上手 | 保姆级](https://www.bilibili.com/video/BV1ja411u7zk?p=1)

## 基础
```bash
# 在git中，HEAD表示当前最新版本
# HEAD~表示上一个版本
# HEAD~2表示前两个版本

# 将当前文件夹设置为仓库
git init
# 在当前文件夹下创建名为repo的仓库
git init repo

# 查看仓库状态
git status
git status -s  # s表示short，简略版

# 添加文件到暂存区
git add file.txt
# 可以使用通配符
git add *.txt
# 将当前目录中的所有文件添加到暂存区
git add .

# 从暂存区移除
git rm --cached file.txt

# 同时删除暂存区和工作区的某个文件
git rm file.txt

# 提交暂存区中的文件到仓库中
git commit -m "这里写提交的文本信息"

# 查看提交记录
git log
git log --oneline  # 简洁版

# 回退版本
git reset --soft <版本ID>  # 回退到<版本ID>，并且不删除工作区和暂存区中的内容
git reset --hard <版本ID>  # 回退，同时删除工作区和暂存区中的内容（慎用）
git reset --mixed <版本ID>  # 回退，删除暂存区内容，不删除工作区（不加--参数的话，默认就是--mixed）

# 回退到低阶版本之后无法用git log查看高阶版本的ID，需要使用：
git reflog  # 来查看高阶版本的ID

# 查看差异
git diff  # 工作区 vs 暂存区
git diff HEAD  # 工作区+暂存区 vs 本地仓库
git diff --cached  # 暂存区 vs 本地仓库
git diff --staged  # 同上
git diff <commit_hash> <commit_hash>  # 比较提交之间的差异
git diff HEAD~ HEAD  # 比较最新的两个提交之间的差异
git diff <brance_name> <branch_name>  # 比较分支之间的差异

# 查看某次提交时某个文件的内容
git show <版本ID>:<文件名>

# 查看某次提交时某个文件的修改内容
git show <版本ID> -- <文件名>

# .gitignore 忽略文件
# 在仓库目录下新建.gitignore文件
# 在.gitignore文件中写入不想纳入版本管理的文件
# 可以使用通配符
# 可以用/Debug/*来实现屏蔽Debug文件夹下的所有文件（好像不加*也行）
# 还是参考视频：https://www.bilibili.com/video/BV1HM411377 吧。
```

## 分支
```bash
git branch  # 查看当前所有分支，*master表现现在正处于master分支上
git branch -v  # 查看所有分支（详细版）

git branch <分支名>  # 创建新分支

git checkout <分支名>  # 切换分支（切换分支时，要保证当前分支没有未提交的修改，否则切换失败）
```

## 远程仓库
```bash
# 在当前文件夹中clone远程仓库
git clone <remote-repo-url>


# 为远程仓库起个别名
git remote add <url别名> <remote-repo-url>  # url别名通常取为“origin”

# 把本地仓库的某分支添加到远程仓库中
git push <远程仓库名> <本地分支名>:<远程仓库分支名>

# push实际上执行了“推送”、“合并”两个步骤，所以如果发生冲突，要手动解决


# 远程仓库比本地仓库版本新，此时要让本地仓库与远程仓库同步，使用git pull
git pull <远程主机名> <远程分支名>:<本地分支名>
```