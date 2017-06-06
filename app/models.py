# -*- coding:utf-8 -*-
from . import db,login_manager
from datetime import datetime
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash,check_password_hash
from flask import request,current_app
import hashlib


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)


	
class Role(db.Model):
	__tablename__='roles'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(64),unique=True)
	permissions=db.Column(db.Integer)
	user=db.relationship('User',backref='role')
	
	@staticmethod
	def insert_roles():
		roles={'User':Permission.FOLLOW | Permission.COMMENT | 
					 Permission.WRITE_ARTICLES,
			  'Moderator':Permission.FOLLOW | Permission.COMMENT |
						  Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,
			  'Administrator':0xff}
			  
		for role in roles:
			r=Role.query.filter_by(name=role).first()
			if r is None:
				r=Role(name=role)
			r.permissions=roles[role]
			db.session.add(r)
		db.session.commit()
	
	def __repr__(self):
		return '<Role %s>'%self.name
		
			  
class Permission:
	FOLLOW=0X01
	COMMENT=0x02
	WRITE_ARTICLES=0x04
	MODERATE_COMMENTS=0X08
	ADMINISTER=0X80
	
class Message(db.Model):
	__tablename__='messages'
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.String(128))
	sender_id=db.Column(db.Integer,db.ForeignKey('users.id'))
	recipent_id=db.Column(db.Integer,db.ForeignKey('users.id'))
	timestamp=db.Column(db.DateTime,default=datetime.utcnow)
	confirmed=db.Column(db.Boolean,default=False)
	
class Comment(db.Model):
	__tablename__='comments'
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.Text)
	timestamp=db.Column(db.DateTime,default=datetime.utcnow)
	disable=db.Column(db.Boolean)
	confirmed=db.Column(db.Boolean,default=False)
	article_id=db.Column(db.Integer,db.ForeignKey('articles.id'))
	author_id=db.Column(db.String,db.ForeignKey('users.id'))
	recipent_id=db.Column(db.String,db.ForeignKey('users.id'))
	
	
class User(db.Model,UserMixin):
	__tablename__='users'
	id=db.Column(db.Integer,primary_key=True)
	email=db.Column(db.String(64),unique=True)
	username=db.Column(db.String(64),unique=True)
	password_hash=db.Column(db.String(128))
	confirmed=db.Column(db.Boolean,default=False)
	name=db.Column(db.String(64))
	location=db.Column(db.String(64))
	about_me=db.Column(db.String(64))
	since=db.Column(db.DateTime,default=datetime.utcnow)
	last_login=db.Column(db.DateTime,default=datetime.utcnow)
	role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
	articles=db.relationship('Article',backref='author',lazy='dynamic')
	comments=db.relationship('Comment',foreign_keys=[Comment.author_id],
			 backref='author',lazy='dynamic')
	
	commented=db.relationship('Comment',foreign_keys=[Comment.recipent_id],
			  backref='recipent',lazy='dynamic')
	collection_of_articles=db.relationship('Article',secondary='collects',backref=db.backref('collectors',lazy='dynamic'),
							lazy='dynamic')
	
	sender=db.relationship('Message',
						   foreign_keys=[Message.sender_id],
						   backref=db.backref('recipent',lazy='joined'),
						   lazy='dynamic',
						   cascade='all,delete-orphan')
	recipent=db.relationship('Message',foreign_keys=[Message.recipent_id],
							 backref=db.backref('sender',lazy='joined'),
							 lazy='dynamic',cascade='all,delete-orphan')
	
	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email=='122744952@qq.com':
				self.role=Role.query.filter_by(name='Administrator').first()
			if self.role is None:
				self.role=Role.query.filter_by(name='User').first()
			
	def can(self,permission):
		return self.role is not None and \
		       (self.role.permissions & permission) == permission
		
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)
		
	@property
	def password(self):
		raise AttributeError("password属性不可访问")
		
	@password.setter
	def password(self,passwd):
		self.password_hash=generate_password_hash(passwd)
		
	def check_password(self,passwd):
		return check_password_hash(self.password_hash,passwd)
		
	def generate_token(self):
		s=Serializer(current_app.config['SECRET_KEY'],expires_in=600)
		return s.dumps({'confirm':self.id})
		
	def confirmed_token(self,token):
		s=Serializer(current_app.config['SECRET_KEY'])
		try:
			data=s.loads(token)
		except:
			return False
		return True
		
	def ping(self):
		self.last_login=datetime.utcnow()
		db.session.add(self)
	
		
	def collect(self,article):
		if not self.is_collect(article):
			c=Collect(user_id=self.id,article_id=article.id)
			db.session.add(c)
			
	def uncollect(self,article):
		if self.is_collect(article):
			c=Collect.query.filter_by(user_id=self.id,article_id=article.id).first()
			db.session.delete(c)
			
	def is_collect(self,article):
		c=Collect.query.filter_by(user_id=self.id,article_id=article.id).first()
		return c is not None
	
	def collect_timestamp(self,article):
		c=Collect.query.filter_by(user_id=self.id,article_id=article.id).first()
		return c.timestamp
	
	
	
	
	
	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py
		
		seed()
		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     since=forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()
				
	def __repr__(self):
		return '<User %s>'%self.username
		
		
#私信	
	def unreadmessages(self):
		return self.sender.filter_by(confirmed=False).count()
		
	def lastmessage(self):
		return self.sender.all()[-1].body
		
	def lastmessageform(self):
		return self.sender.all()[-1].sender
		

#评论		
	def unreadcommenteds(self):
		return Comment.query.join(Article,Article.id==Comment.article_id) \
			   .filter(Article.author_id==self.id).count()
			   
	def lastcomment(self):
		return Comment.query.join(Article,Article.id==Comment.article_id) \
			   .filter(Article.author_id==self.id).all()[-1]
			   
	def lastcommentform(self):
		return Comment.query.join(Article,Article.id==Comment.article_id) \
			   .filter(Article.author_id==self.id).all()[-1].author
			   
	def gravatar(self,size=100,default='identicon',rating='g'):
		if request.is_secure:
			url='https://secure.gravatar.com/avatar'
		else:
			url='http://www.gravatar.com/avatar'
		hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
				url=url,hash=hash,size=size,default=default,rating=rating)
		
	

	
	
	
class Article(db.Model):
	__tablename__='articles'
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(128))
	body=db.Column(db.Text)
	visit=db.Column(db.Integer,default=0)
	timestamp=db.Column(db.DateTime,default=datetime.utcnow)
	author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
	comments=db.relationship('Comment',backref='article',lazy='dynamic')
	category_id=db.Column(db.Integer,db.ForeignKey('categories.id'))
	
	@staticmethod
	def hot_articles():
		articles=Article.query.all()
		return sorted(articles,key=lambda x: x.visit,reverse=True)[0:10]
		
							  
	def is_collected(self,user):
		c=self.collector.filter_by(user_id=user.id).first()
		return c is not None
		
	def __repr__(self):
		return '<Article %s>'%self.body
	
	@staticmethod
	def hot_article():
		hot=Article.query.order_by(Article.comments.count().desc()).all()[0:10]
		
	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed,randint
		import forgery_py
		
		seed()
		user_count = User.query.count()
		category_count=Category.query.count()
		for i in range(count):
			u = User.query.offset(randint(0, user_count - 1)).first()
			ca = Category.query.offset(randint(0, category_count - 1)).first()
			p = Article(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
						timestamp=forgery_py.date.date(True),
						author=u,category=ca)
			db.session.add(p)
			db.session.commit()
			
	def __repr__(self):
		return '<Article %s>'%self.id

class Collect(db.Model):
	__tablename__='collects'
	user_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	article_id=db.Column(db.Integer,db.ForeignKey('articles.id'),primary_key=True)
	timestamp=db.Column(db.DateTime(),default=datetime.utcnow)
	
	def __repr__(self):
		return '<Collect user_id:%s,article_id:%s >'%(self.user_id,self.article_id)
	


	
class Category(db.Model):
	__tablename__='categories'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String,unique=True)
	articles=db.relationship('Article',backref='category',lazy='dynamic')
	
	@staticmethod
	def insert_category():
		categorylist = ["Python","Web","Linux","数据库","前端","杂记"]
		for category in categorylist:
			c=Category.query.filter_by(name=category).first()
			if c is None:
				c=Category(name=category)
			db.session.add(c)
		db.session.commit()
		
class AnonymousUser(AnonymousUserMixin):
	def can(self,perimission):
		return False
		
	def is_administrator(self):
		return False
		
	def confirmed_token(self,token):
		s=Serializer(current_app.config['SECRET_KEY'])
		try:
			data=s.dumps(token)
		except:
			return False
		return True
		
login_manager.anonymous_user=AnonymousUser
		
	
	