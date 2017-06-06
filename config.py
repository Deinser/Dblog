import os

name=os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY='deinser'
	MAIL_SERVER='smtp.qq.com'
	MAIL_PORT=465
	MAIL_USE_SSL=True
	MAIL_USERNAME='122744952@qq.com'
	MAIL_PASSWORD='bktfpxefbjhebgeg'
	DBLOG_ADMIN='122744952@qq.com'
	
	@staticmethod
	def init_app():
		pass

class DevelopmentConfig(Config):
	DEBUG=True
	SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(name,'dev.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	
class TestingConfig(Config):
	Testing=True
	SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(name,'test.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(name,'production.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	
config={'development':DevelopmentConfig,
		'testing':TestingConfig,
		'production':ProductionConfig,
		'default':DevelopmentConfig}