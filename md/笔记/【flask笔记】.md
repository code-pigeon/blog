# flask笔记
## 模板继承
`_header.html`：
```html
<div>
    <a href="https://www.baidu.com">百度</a>
    <a href="https://www.bilibili.com">B站</a>
</div>
```

`index.html`：
```html
<p>通过下面方法添加别的模板文件</p>
{% include '_header.html' %}
```

> 部分模板一般用下划线开头，与完整的模板区分开来。

## 引入静态文件
用`url_for`函数：
```html
<img src="{{ url_for('static', filename='img/OIP-C.jpeg') }}" alt="test">
```
`static/<filename>`会被flask自动整成一个路由，可以通过`域名/static/<filename>`来访问静态文件。

## Bootstrap
[链接](https://getbootstrap.com/docs/4.0/getting-started/download/)
好像是个前端框架：Bootstrap是一个流行的前端开发框架，它提供了一系列的HTML、CSS和JavaScript工具，用于快速构建响应式网站和Web应用程序。

## 表单
要使用的库
```python
from flask import request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
```
先在app.py里定义表单类：
```python
class LoginForm(FlaskForm):
    # StringField 构造函数中的可选参数 validators 指定一个由验证函数组成的列表，在接受
    # 用户提交的数据之前验证数据。验证函数 Required() 确保提交的字段不为空。
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    # SubmitField 类表示属性为 type="submit" 的 <input> 元素
    submit = SubmitField(label='Log in')
```
接着需要在路由中使用该表单类：
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
    	# 处理表单数据
        print(request.form.get('username'))
    return render_template('login.html', form=form)
```
同时在html文件中也要使用定义的表单：
```html
<form method="post">
    {{ form.csrf_token }}
    {{ form.username.label }}{{ form.username }}<br>
    {{ form.password.label }}{{ form.password }}<br>
    {{ form.submit }}<br>
</form>
```