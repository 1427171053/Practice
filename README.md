# Practice
 项目描述

这是一个实践项目，使用 Python Flask 框架连接数据库，并配置了一级缓存、二级缓存、Nginx 反向代理，还进行了微服务的拆分。account_service.py 和 projects_service.py 是两个基于微服务思想构建的服务，一个是账号服务，负责进行账号的注册登陆，另外一个是项目和参与者服务，负责连接数据库之后的增删改查操作，这两个服务之间构建了内部通信的 API，其中Nginx配置文件是nginx.conf.测试这两个微服务，我使用的是postman

前置条件

要使用这两个程序，需要安装以下软件和库：

软件要求

	1.	Python 3
	2.	pip（Python 包管理工具）
	3.	PostgreSQL
	4.	Redis
	5.	Nginx

Python 包

你需要安装以下 Python 包来支持你的 Flask 应用：

	1.	Flask: 主框架
	2.	Flask-SQLAlchemy: 数据库集成
	3.	Werkzeug: 密码哈希处理
	4.	PyJWT: 处理 JSON Web Token (JWT)
	5.	redis: 处理 Redis 连接
	6.	requests: 进行 HTTP 请求
	7.	logging: 已经是 Python 标准库的一部分，无需安装

除此之外我还用form表单，做了个前后端结合的简单小项目，里面涉及连接数据库之后的增删改查操作和简单的页面，以及登陆，文件名是app.py
登陆的账号是admin
密码是admin