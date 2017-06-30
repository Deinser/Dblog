# -*- coding:utf-8 -*-
from app import create_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from app.models import User,Role,Article,Comment,Collect,Category,Message
from app import db
import os
                                                                                                       



app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)
migrate=Migrate(app,db)


@manager.shell
def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role,Article=Article,Comment=Comment,
				Collect=Collect,Category=Category,Message=Message)

manager.add_command('db',MigrateCommand)


@manager.command
def datainit():
	from app.models import Role,User,Article,Category
	print('Category init')
	Category.insert_category()
	print('Role init')
	Role.insert_roles()
	print('User and Article generate')
	User.generate_fake(50)
	Article.generate_fake(50)
	


@manager.command
def test():
	"""运行单元测试"""
	import unittest
	tests=unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	

@manager.command
def deploy():
	"""运行部署任务"""
	from flask_migrate import upgrade
	from app.models import Role,Category

	upgrade()

	Role.insert_roles()

	Category.insert_category()



if __name__=='__main__':
	manager.run()