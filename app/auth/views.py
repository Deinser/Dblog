# -*- coding:utf-8 -*- 
from . import auth
from .. import db
from ..models import User
from .forms import RegisterForm,LoginForm,ChangePasswordForm, \
				   ResetRequestForm,ResetPasswordForm,ResetEmailForm
from flask import render_template,request,flash,url_for,redirect,current_app
from flask_login import current_user,login_user,logout_user,login_required
from ..mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()






@auth.route('/register',methods=['GET','POST'])
def register():
	form=RegisterForm()
	if form.validate_on_submit():
		user1=User.query.filter_by(email=form.email.data).first()
		user2=User.query.filter_by(username=form.username.data).first()
		if user1 is not None:
			flash('邮箱已经被注册')
			return redirect(url_for('auth.register'))
		if user2 is not None:
			flash('用户名已经被注册')
			return redirect(url_for('auth.register'))
		user=User(email=form.email.data,
				  username=form.username.data,
				  password=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('注册成功')
		login_user(user)
		return redirect(url_for('main.index'))
	return render_template('auth/register.html',form=form)
	
@auth.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()
	
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is not None and user.check_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('无效用户名或密码')	
	return render_template('auth/login.html',form=form)
	
@auth.route('/logout')
def logout():
	logout_user()
	flash('退出登录')
	return redirect(url_for('main.index'))
	
@auth.route('/change-userset',methods=['GET','POST'])
@login_required
def change_userset():
	form=ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.check_password(form.old_password.data):
			current_user.password=form.new_password.data
			db.session.add(current_user)
			flash('密码修改成功')
			return redirect(url_for('main.index'))
		else:
			flash('密码错误')
			return redirect(url_for('auth.change_userset'))
	return render_template('auth/change_userset.html',form=form)
	
@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
	form=ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.check_password(form.old_password.data):
			current_user.password=form.new_password.data
			db.session.add(current_user)
			flash('密码修改成功')
			return redirect(url_for('main.index'))
		else:
			flash('密码错误')
			return redirect(url_for('auth.change_userset'))
	return render_template('auth/change_password.html',form=form)
	

@auth.route('/request/reset-password',methods=['GET','POST'])
def password_reset_request():
	if not current_user.is_authenticated:
		form=ResetRequestForm()
		if form.validate_on_submit():
			user=User.query.filter_by(email=form.email.data).first()
			if user is None:
				flash('该Email还没注册')
				return redirect(url_for('auth.password_reset_request'))
			token=user.generate_token()	
			send_mail('重设密码',user.email,'auth/mail/reset_password',
					user=user,token=token)
			flash('验证邮件已发送')
		return render_template('auth/reset_password.html',form=form)
	else:
		token=current_user.generate_token()	
		send_mail('重设密码',current_user.email,'auth/mail/reset_password',
				user=current_user,token=token)
		flash('验证邮件已发送')
		return render_template('auth/mail/reset_password.html',user=current_user)
		
				
@auth.route('/reset-password/<token>',methods=['GET','POST'])
def password_reset(token):
	if not confirmed_token(token):
		flash('链接无效或者已经过期')
		return redirect(url_for('main.index'))
	s=Serializer(current_app.config['SECRET_KEY'])
	data=s.loads(token)
	form=ResetPasswordForm()
	if form.validate_on_submit():
		user=User.query.get(data.get('confirm'))
		user.password=form.password.data
		db.session.add(user)
		login_user(user)
		flash('重设密码成功')
		return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)
	
@auth.route('/request/change-email')
@login_required
def change_email_request():
	token=current_user.generate_token()
	send_mail('修改Email地址',current_user.email,'auth/mail/change_email',
			  user=current_user,token=token)
	flash('修改Email验证邮件已发送')
	return render_template('auth/mail/change_email.html',user=current_user)
	
@auth.route('/change-email/<token>',methods=['GET','POST'])
@login_required
def change_email(token):
	if not confirmed_token(token):
		flash('链接无效或者已经过期')
		return redirect(url_for('main.index'))
	s=Serializer(current_app.config['SECRET_KEY'])
	data=s.loads(token)
	form=ResetEmailForm()
	if form.validate_on_submit():
		current_user.email=form.email.data
		if current_user != User.query.get(data.get('confirm')):
			flash('不能修改其他用户的Email')
			return redirect(url_for('main.index'))
		db.session.add(current_user)
		flash('Email修改成功')
		return redirect(url_for('main.index'))
	return render_template('auth/change_email.html',form=form)

	

def confirmed_token(token):
		s=Serializer(current_app.config['SECRET_KEY'])
		try:
			data=s.loads(token)
		except:
			return False
		return True
	
		
		
		
	
	
	
	
	
		
		
			
			
	