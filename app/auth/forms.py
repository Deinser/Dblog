 # -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from ..models import User
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import Required,Email,EqualTo,Regexp,Length,ValidationError

class RegisterForm(FlaskForm):
	email=StringField('电子邮箱：',
					  validators=[Required(),Email('电子邮件格式错误'),Length(5,30)])
	username=StringField('用户名：',validators=[Required(),
						 Regexp(r'^[0-9a-zA-Z][0-9a-zA-Z\_]{4,19}$',0,
						 '用户名由5-20为字母、数字、下划线组成')])
	password=PasswordField('密码:',validators=[Required(),Length(5,20),
	                       EqualTo('password2',message='两次输入的密码不匹配')])
	password2=PasswordField('确认密码:',validators=[Required()])
	submit=SubmitField('注册')
	
	password=PasswordField('密码:',validators=[Required(),
	                       EqualTo('password2',message='Passwords must match.')])
	password2=PasswordField('确认密码：',validators=[Required()])
	submit=SubmitField('注册')
	
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email已经被注册')
		
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经被注册')
	
class LoginForm(FlaskForm):
	email=StringField('电子邮箱',validators=[Required(),Email(),Length(5,30)])
	password=PasswordField('密码',validators=[Required(),Length(5,20)])
	remember_me=BooleanField('记住我')
	submit=SubmitField('登录')
	
class ChangePasswordForm(FlaskForm):
	old_password=PasswordField('旧密码:',validators=[Required()])
	new_password=PasswordField('新密码:',validators=[Required(),EqualTo('new_password2',message='两次输入的密码不匹配')])
	new_password2=PasswordField('确认新密码:',validators=[Required()])
	submit=SubmitField('提交')
	
class ResetRequestForm(FlaskForm):
	email=StringField('Email:',validators=[Required(),Email('Email格式错误')])
	submit=SubmitField('提交')
	
class ResetPasswordForm(FlaskForm):
	password=PasswordField('新密码：',validators=[Required(),EqualTo('password2',
						   message='两次输入的密码不匹配')])
	password2=PasswordField('确认密码：',validators=[Required()])
	submit=SubmitField('提交')
	
class ResetEmailForm(FlaskForm):
	email=StringField('新Email:',validators=[Required(),Email('Email格式错误')])
	submit=SubmitField('提交')
	
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email已经被注册')
	
	
	