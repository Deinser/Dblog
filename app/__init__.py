from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import config
from flask_pagedown import PageDown
from flask_mail import Mail




moment=Moment()
db=SQLAlchemy()
bootstrap=Bootstrap()
login_manager=LoginManager()
pagedown=PageDown()
mail=Mail()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'
login_manager.login_message='请先登录.'

def create_app(config_name):
	app=Flask(__name__)
	app.config.from_object(config[config_name])
	
	if not app.debug and not app.testing and not app.config['SSL_DISABLE']
		from flask_sslify import SSLify
		sslify=SSLify(app)
	
	moment.init_app(app)
	db.init_app(app)
	bootstrap.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)
	mail.init_app(app)
	
	
	from .auth import auth
	from .main import main
	from .admin import admin
	
	app.register_blueprint(main)
	app.register_blueprint(auth,url_prefix='/auth')
	app.register_blueprint(admin,url_prefix='/admin')
	
	return app
	
	

	



