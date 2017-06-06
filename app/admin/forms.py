from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,SelectField,TextField
from wtforms.validators import Required,Email,EqualTo,ValidationError,Length
from ..models import User,Category

class AddadminForm(FlaskForm):
	username=StringField('用户名：',validators=[Required()])
	password=PasswordField('密码：',validators=[Required(),EqualTo('password2',
			 message='两次输入的密码不匹配')])
	password2=PasswordField('确认密码：',validators=[Required()])
	submit=SubmitField('提交')
	
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经被注册')
			
		
class AddcategoryForm(FlaskForm):
	name=StringField('分类名称',validators=[Required()])
	submit=SubmitField('提交')
	
	def validate_name(self,field):
		if Category.query.filter_by(name=field.data).first():
			raise ValidationError('分类已经存在')  
			
			
