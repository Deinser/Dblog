# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextField,SelectField,BooleanField,PasswordField
from wtforms.validators import Required,Length,Email
from ..models import Category



class ArticleForm(FlaskForm):
	category=SelectField('分类',coerce=int)
	title=StringField('标题',validators=[Required(),Length(1,20)])
	body=TextField('正文',validators=[Required()])
	submit=SubmitField('提交')
	
	def __init__(self,*args,**kwargs):
		super(ArticleForm,self).__init__(*args,**kwargs)
		self.category.choices=[(category.id,category.name) for category in \
							    Category.query.order_by(Category.name).all()]
	
class CommentForm(FlaskForm):
	body=TextField('',validators=[Required()])
	submit=SubmitField('发表')
	
class MessageForm(FlaskForm):
	body=TextField('内容',validators=[Required()])
	submit=SubmitField('发送')
	
class SearchForm(FlaskForm):
	search=StringField('搜索',validators=[Required()])
	
class EditProfileForm(FlaskForm):
	name=StringField('姓名：',validators=[Required()])
	location=StringField('居住地：',validators=[Required()])
	about_me=StringField('一句话介绍自己：',validators=[Required()])
	submit=SubmitField('提交')
	
class EditProfileAdminForm(FlaskForm):
	email=StringField('电子邮箱：',validators=[Required(),Email('电子邮箱格式错误')])
	username=StringField('用户名：',validators=[Required()])
	password=PasswordField('密码：',validators=[Required()])
	name=StringField('姓名')
	role=SelectField('角色',coerce=int)
	confirmed=BooleanField('Confirmed')
	location=StringField('居住地：')
	about_me=StringField('简介')
	submit=SubmitField('提交')
	
	def __init__(self,user,*args,**kwargs):
		super(EditProfileAdminForm,self).__init__(*args,**kwargs)
		self.user=user
		self.role.choices =[(role.id,role.name) 
							for role in Role.query.order_by(Roel.name).all()]
	def validate_email(self,field):
		if field.data == self.user.email and \
						 User.query.filter_by(email=field.data).first():
			raise ValidationError('Email已经存在')
			
	def validate_username(self,field):
		if field.data == self.user.username and \
						 User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经存在')
			
		
	
	
	