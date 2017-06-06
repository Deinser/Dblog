from flask import render_template,url_for
from . import main


@main.app_errorhandler(404)
def not_found_page(e):
	return render_template('404.html'),404
	
@main.app_errorhandler(500)
def server_error(e):
	return render_template('500.html'),500
	
@main.app_errorhandler(403)
def forbidden_error(e):
	return render_template('403.html'),403