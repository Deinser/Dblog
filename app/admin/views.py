# -*- coding:utf-8 -*-
from . import admin
from .forms import AddadminForm,AddcategoryForm
from ..models import User,Comment,Article,Category,Role,Permission
from flask import render_template,redirect,request,url_for,flash
from flask_login import login_required,current_user
from ..decorator import admin_required
from .. import db



@admin.route('/')
@login_required
@admin_required
def edit():
	page=request.args.get('page',1,type=int)
	pagination=User.query.filter_by(role_id=2).order_by(User.since.desc()).paginate(
			   page,per_page=20,error_out=False)
	moderators=pagination.items
	return render_template('admin/edit.html',moderators=moderators,pagination=pagination,page=page)


@admin.route('admin2user/<int:id>')
@login_required
@admin_required
def admin2user(id):
	user=User.query.get_or_404(id)
	user.role=Role.query.filter_by(name='User').first()
	db.session.add(user)
	flash('%s 已经被降为普通用户'%user.username)
	return redirect(url_for('admin.edit',page=request.args.get('page',1,type=int)))
	

@admin.route('/addadmin',methods=['GET','POST'])
@login_required
@admin_required
def addadmin():
	form=AddadminForm()
	if form.validate_on_submit():
		user=User(email=form.username.data+'@Dblog.com',
				  username=form.username.data,
				  password=form.password.data,
				  confirmed=True,
				  role=Role.query.filter_by(id=2).first())
		db.session.add(user)
		flash('已添加%s为管理员'%user.username)
		return redirect(url_for('admin.edit'))
	return render_template('admin/addadmin.html',form=form)
	

@admin.route('/edituser')
@login_required
@admin_required
def edituser():
	page=request.args.get('page',1,type=int)
	pagination=User.query.order_by(User.since.desc()).paginate(
			   page,per_page=20,error_out=False)
	users=pagination.items
	return render_template('admin/edituser.html',pagination=pagination,
							page=page,users=users)
							

@admin.route('/deleteuser/<int:id>')
@login_required
@admin_required
def deleteuser(id):
	user=User.query.get_or_404(id)
	articles=user.articles
	for article in articles:
		db.session.delete(article)
	comments=user.comments
	for comment in comments:
		db.session.delete(comment)
	db.session.delete(user)
	flash('已经将%s删除'%user.username)
	return redirect(url_for('admin.edituser'))
	

@admin.route('/article')
@login_required
@admin_required
def editarticle():
	page=request.args.get('page',1,type=int)
	pagination=Article.query.order_by(Article.timestamp.desc()).paginate(
				page,per_page=20,error_out=False)
	articles=pagination.items
	return render_template('admin/editarticle.html',page=page,
							pagination=pagination,articles=articles)


@admin.route('/deletearticle/<int:id>')
@login_required
@admin_required
def deletearticle(id):
	article=Article.query.get_or_404(id)
	comments=article.comments
	for comment in comments:
		db.session.delete(article)
	db.session.delete(article)
	flash('已将博客和相关的评论删除')
	return redirect(url_for('admin.editarticle',page=request.args.get('page',1,type=int)))
	

@admin.route('/editcategory')
@login_required
@admin_required
def editcategory():
	category=Category.query.all()
	return render_template('admin/editcategory.html',categorys=category)
	

@admin.route('/addcategory',methods=['GET','POST'])
@login_required
@admin_required
def addcategory():
	form=AddcategoryForm()
	if form.validate_on_submit():
		category=Category(name=form.name.data)
		db.session.add(category)
		flash('添加成功')
		return redirect(url_for('admin.editcategory'))
	return render_template('admin/addcategory.html',form=form)
	

@admin.route('/editcomment')
@login_required
@admin_required
def editcomment():
	page=request.args.get('page',1,type=int)
	pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(
			page,per_page=20,error_out=False)
	comments=pagination.items
	return render_template('admin/editcomment.html',pagination=pagination,
							comments=comments,page=page)


@admin.route('/deletecomment/<int:id>')
@login_required
@admin_required
def delete_comment(id):
	comment=Comment.query.get_or_404(id)
	db.session.delete(comment)
	flash('删除成功') 
	return redirect(url_for('.editcomment',page=request.args.get('page',1,type=int)))
	

@admin.route('/enable-comment/<int:id>')
@login_required
@admin_required
def enable_comment(id):
	comment=Comment.query.get_or_404(id)
	comment.disable=False
	db.session.add(comment)
	flash('恢复成功')
	return redirect(url_for('.editcomment',page=request.args.get('page',1,type=int)))


@admin.route('/disable-comment/<int:id>')
@login_required
@admin_required
def disable_comment(id):
	comment=Comment.query.get_or_404(id)
	comment.disable=True
	db.session.add(comment)
	flash('屏蔽成功')
	return redirect(url_for('.editcomment',page=request.args.get('page',1,type=int)))
	
	
	
	
			
	
		
	
	
	
	
	
	
	
	