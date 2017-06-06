from . import mail
from flask_mail import Message
from threading import Thread
from flask import render_template,current_app

def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)
		
def send_mail(subject,to,template,**kwargs):
	app = current_app._get_current_object()
	msg=Message('[Blog]'+subject,sender='122744952@qq.com',recipients=[to])
	msg.body=render_template(template+'.txt',**kwargs)
	thr=Thread(target=send_async_email,args=[app,msg])
	thr.start()
	return thr

	

