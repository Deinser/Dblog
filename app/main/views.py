# -*- coding:utf-8 -*-
from . import main
from datetime import datetime
from flask import render_template,redirect,url_for,request,g,abort,flash,session
from flask_login import current_user,login_required
from ..models import User,Role,Article,Comment,Message,Collect,Permission,Category
from .forms import ArticleForm,CommentForm,MessageForm,SearchForm,EditProfileForm,EditProfileAdminForm
from ..decorator import permission_required,admin_required
from .. import db
import math


#全局变量
@main.before_app_request
def before_request():
	g.search_form=SearchForm()
	g.categorys=Category.query.all()
	g.hot_articles=Article.hot_articles()
	g.current_time=datetime.utcnow()

	
@main.route('/')
def index():
	page=request.args.get('page',1,type=int)
	pagination=Article.query.order_by(Article.timestamp.desc()).paginate(
				page,per_page=15,error_out=False)
	articles=pagination.items
	return render_template('index.html',pagination=pagination,articles=articles)
	

	
@main.route('/user/<username>')
def user(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('该用户不存在')
		return redirect(url_for('main.index'))
	page=request.args.get('page',1,type=int)
	pagination=user.articles.order_by(Article.timestamp.desc()).paginate(
				page,per_page=15,error_out=False)
	articles=pagination.items
	return render_template('user.html',user=user,pagination=pagination,
							page=page,articles=articles)
	

	
@main.route('/about')
def about_me():
	return render_template('aboutme.html')
	

	
@main.route('/write-article',methods=['GET','POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def write_article():
	form=ArticleForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		article=Article()
		article.category=Category.query.get(form.category.data)
		article.title=form.title.data
		article.body=form.body.data
		article.author=current_user._get_current_object()
		db.session.add(article)
		db.session.commit()
		flash('提交成功')
		return redirect(url_for('.index'))
	return render_template('write_articlea.html',form=form)


	
@main.route('/article/<int:id>',methods=['GET','POST'])	
def article(id):
	form=CommentForm()
	article=Article.query.get_or_404(id)
	article.visit += 1 
	if form.validate_on_submit(): 
		comment=Comment(body=form.body.data,
						article=article,
						author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash('评论成功')
		return redirect(url_for('main.article',id=id,page=-1))
	page=request.args.get('page',1,type=int)
	if page==-1:
		page=math.ceil((article.comments.count())/20)
	pagination=article.comments.order_by(Comment.timestamp.desc()).paginate(
			   page,per_page=20,error_out=False)
	comments=pagination.items
	                                                                                                                                 
	return render_template('article.html',pagination=pagination,form=form,
							comments=comments,articles=[article],page=page)
							
							

@main.route('/article/delete/<int:id>')
@login_required
def delete_article(id):
	article=Article.query.get_or_404(id)
	if article.author != current_user:
		flash('不能删除别人的文章')
		return redirect(url_for('main.index'))
	comments=article.comments
	for comment in comments:
		db.session.delete(comment)
	db.session.delete(article)
	flash('删除成功')
	return redirect(url_for('main.user',username=current_user.username))
	
	

@main.route('/edit-article/<int:id>',methods=['GET','POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def edit_article(id):
	article=Article.query.get_or_404(id)
	if article.author != current_user and \
						 not current_user.can(Permission.ADMINISTER):
		abort(403)
	form=ArticleForm()
	if form.validate_on_submit():
		article.category=Category.query.get(form.category.data)
		article.title=form.title.data
		article.body=form.body.data
		db.session.add(article)
		flash('修改成功')
		return redirect(url_for('main.article',id=article.id))
	form.category.data=article.category_id
	form.title.data=article.title
	form.body.data=article.body
	return render_template('edit_article.html',form=form)
	

	
@main.route('/user/comments/<username>')
def usercomments(username):	
	user=User.query.filter_by(username=username).first()
	page=request.args.get('page',1,type=int)
	pagination=user.comments.order_by(Comment.timestamp.desc()).paginate(
				page,per_page=20,error_out=False)
	comments=pagination.items
	return render_template('user_comments.html',user=user,page=page,
							pagination=pagination,comments=comments)
							
							

@main.route('/delete/comment/<int:id>')
@login_required
def delete_comment(id):
	comment=Comment.query.get_or_404(id)
	db.session.delete(comment)
	flash('评论删除成功')
	return redirect(url_for('.usercomments',username=current_user.username,
                            page=request.args.get('page', 1, type=int)))
	
	

@main.route('/category/<int:id>')
def category(id):
	category=Category.query.get_or_404(id)
	page=request.args.get('page',1,type=int)
	pagination=category.articles.order_by(Article.timestamp.desc()).paginate(
			   page,per_page=20,error_out=False)
	articles=pagination.items
	return render_template('category.html',pagination=pagination,
							articles=articles,page=page,category=category)
							

							
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
	form=EditProfileForm()
	if form.validate_on_submit():
		current_user.name=form.name.data
		current_user.location=form.location.data
		current_user.about_me=form.about_me.data
		db.session.add(current_user)
		flash('资料修改成功')
		return redirect(url_for('main.user',username=current_user.username))
	form.name.data=current_user.name
	form.location.data=current_user.location
	form.about_me.data=current_user.about_me
	return render_template('edit_profile.html',form=form)


	
@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user=User.query.get_or_404(id)
	form=EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email=form.email.data
		user.username=form.username.data
		user.password=form.password.data
		user.name=form.name.data
		user.role=Role.query.get(form.role.data)
		user.confirmed=form.confirmed.data
		user.location=form.location.data
		user.about_me=form.about_me.data
		db.session.add(user)
		return redirect(url_for('main.user',username=user.username))
	form.email.data=user.eamil
	form.username.data=user.username
	form.password.data=user.password	
	form.name.data=user.name
	form.role.data=user.role_id
	form.confirmed.data=user.confirmed
	form.location.data=user.location
	form.about_me.data=user.about_me
	return render_template('edit_profile.html',form=form,user=user)
	

	
@main.route('/collect/<int:id>')
@login_required
def collect(id):
	article=Article.query.get_or_404(id)
	if article is None:
		flash('没有该文章')
		return redirect(url_for('main.index'))
	if current_user.is_collect(article):
		flash('已经收藏过文章了')
		return redirect(url_for('main.index'))
	current_user.collect(article)
	flash('收藏成功')
	return redirect(url_for('main.article',id=id))
	

	
@main.route('/uncollect/<int:id>')
@login_required
def uncollect(id):
	article=Article.query.get_or_404(id)
	if article is None:
		flash('没有该文章')
		return redirect(url_for('main.index'))
	if not current_user.is_collect(article):
		flash('您还没有收藏该文章')
		return redirect(url_for('main.index'))
	current_user.uncollect(article)
	flash('取消成功')
	return redirect(url_for('main.article',id=id))
	

	
@main.route('/<username>/collection_of_articles')
@login_required
def collection_of_articles(username):
	user=User.query.filter_by(username=username).first_or_404()
	articles=user.collection_of_articles
	return render_template('collection_of_articles.html',articles=articles,user=user)
	
	
	
@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page=request.args.get('page',1,type=int)
	pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(
			 page,per_page=20,error_out=False)
	comments=pagination.items
	return render_template('moderate.html',pagination=pagination,comments=comments,page=page)


	
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment=Comment.query.get_or_404(id)
	comment.disable=True
	db.session.add(comment)
	flash('屏蔽成功')
	return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))
	

	
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment=Comment.query.get_or_404(id)
	comment.disable=False
	db.session.add(comment)
	flash('恢复成功')
	return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))


	
@main.route('/shownotice')
@login_required
def shownotice():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=20,error_out=False)
    comments = pagination.items
    return render_template('shownotice.html', comments=comments,
                           pagination=pagination, page=page)
						   

						   
@main.route('/shownotice/unconfirmed/<int:id>')
@login_required
def shownotice_unconfirmed(id):
    comment = Comment.query.get_or_404(id)
    comment.confirmed = True
    db.session.add(comment)
    return redirect(url_for('.shownotice',
                            page=request.args.get('page', 1, type=int)), )



@main.route('/shownotice/confirmed/<int:id>')
@login_required
def shownotice_confirmed(id):
    comment = Comment.query.get_or_404(id)
    comment.confirmed = False
    db.session.add(comment)
    return redirect(url_for('.shownotice',
                            page=request.args.get('page', 1, type=int)), )
		
	
	
@main.route('/video')
def video():
	return render_template('video.html')
	

	
@main.route('/admin')
@login_required
@permission_required(Permission.ADMINISTER)
def admin():
	return render_template('admin.html')
	

	
@main.route('/send-message/<int:id>',methods=['GET','POST'])
@login_required
@permission_required(Permission.COMMENT)
def send_message(id):
	recipent=User.query.get_or_404(id)
	form=MessageForm()
	if form.validate_on_submit():
		m=Message()
		m.sender=current_user._get_current_object()
		m.recipent=recipent
		m.body=form.body.data
		db.session.add(m)
		flash('私信发送成功')
		form.body.data=''
		return redirect(url_for('main.send_message',id=id))
	return render_template('sendmessage.html',form=form,id=id,recipent=recipent)
	

	
@main.route('/showmessage')
@login_required
def show_message():
	user=User.query.filter_by(username=current_user.username).first_or_404()
	page=request.args.get('page',1,type=int)
	pagination=user.sender.order_by(Message.timestamp.desc()).paginate(
			   page,per_page=20,error_out=False)
	messages=pagination.items
	return render_template('showmessage.html',pagination=pagination,
						   messages=messages,page=page)


						   
@main.route('/message/unconfirmed/<int:id>')
@login_required
def showmessage_unconfirmed(id):
	message=Message.query.get_or_404(id)
	if message.recipent != current_user:
		abort(403)
	message.confirmed=True
	db.session.add(message)
	return redirect(url_for('main.show_message',page=request.args.get('page',1,type=int)))
	
	

@main.route('/message/confirmed/<int:id>')
@login_required
def showmessage_confirmed(id):
	message=Message.query.get_or_404(id)
	if message.recipent != current_user:
		abort(403)
	message.confirmed=False
	db.session.add(message)
	return redirect(url_for('main.show_message',page=request.args.get('page',1,type=int)))
	


@main.route('/message/delete/<int:id>')
@login_required
def message_delete(id):
	message=Message.query.get_or_404(id)
	if message.recipent != current_user:
		abort(403)
	db.session.delete(message)
	flash('删除成功')
	return redirect(url_for('main.show_message',page=request.args.get('page',1,type=int)))
	
	
	

	
@main.route('/search',methods=['GET','POST'])
def search():
	query=g.search_form.search.data
	articles=[]
	if g.search_form.validate_on_submit():
		articles=Article.query.filter(Article.title.like('%'+query+'%')).all()
	return render_template('search_results.html',articles=articles,query=query)
	
	
	

	
	

	
		
		
	
	
	
							

	
	
	
	
	

		