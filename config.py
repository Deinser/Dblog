# -*- coding:utf-8 -*-
import os

name=os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY='deinser'
	MAIL_SERVER='smtp.qq.com'
	MAIL_PORT=465
	MAIL_USE_SSL=True
	MAIL_USERNAME='122744952@qq.com'
	MAIL_PASSWORD='bktfpxefbjhebgeg'
	DBLOG_MAIL_SENDER='Dblog Admin <122744952@qq.com>'
	DBLOG_ADMIN='122744952@qq.com'
	SSL_DISABLE=True
	
	
	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG=True
	SQLALCHEMY_DATABASE_URI=os.environ.get('DEV_DATABASE_URI') or \
								'sqlite:///'+os.path.join(name,'dev.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	
class TestingConfig(Config):
	Testing=True
	SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URI') or \
								'sqlite:///'+os.path.join(name,'test.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI') or \
								'sqlite:///'+os.path.join(name,'production.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	
	@classmethod
	def init_app(cls,app):
		Config.init_app(app)
		
		#把错误通过电子邮件发给管理员
		from logging.handlers import SMTPHandler
		import logging
		credentials=None
		secure=None
		if getattr(cls,'MAIL_USERNAME',None) is not None:
			credentials=(cls.MAIL_USERNAME,cls.MAIL_PASSWORD)
			if getattr(cls,'MAIL_USE_SSL',None) is not None:
				secure=()
		mail_handler=SMTPHandler(
			mailhost=(cls.MAIL_SERVER,cls.MAIL_PORT),
			fromaddr=cls.DBLOG_MAIL_SENDER,
			toaddrs=[cls.DBLOG_ADMIN],
			subject='[Dblog]'+'Application Error',
			credentials=credentials,
			secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)
		
	
class HerokuConfig(ProductionConfig):
	
	SSL_DISABLE=bool(os.getenv('SSL_DISABLE'))
	
	@classmethod
	def init_app(cle,app):
		ProductionConfig.init_app(app)
		
		import logging
		from logging import StreamHandler
		from werkzeug.contrib.fixers import ProxyFix
		
		
		app.wsgi_app=ProxyFix(app.wsgi_app)
		file_handler=StreamHandler()
		file_handler.setLevel(logging.WARNING)
		app.logging.addHandler(file_handler)
		
		
			
		
	
config={'development':DevelopmentConfig,
		'testing':TestingConfig,
		'production':ProductionConfig,
		'heroku':HerokuConfig,
		'default':DevelopmentConfig}