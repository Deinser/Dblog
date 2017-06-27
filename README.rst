一个基于Python Flask的Blog程序


Prerequests:

1. python3.6
2. Reference: Flask Web开发-基于Python的Web应用开发实战 `http://www.ituring.com.cn/book/1449`

如何安装：
	$ pip install -r requirements.txt  

初始化db:	
	$ python manage.py db init

	$ python manage.py db migrate
	
	$ python manage.py db upgrade

创建测试数据并运行：	
	$ python manage.py datainit

	$ python manage.py runserver