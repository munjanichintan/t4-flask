from flask import Flask, request, jsonify, make_response, session, app, Response,url_for, Blueprint
from ecommerceapp import app, db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate, MigrateCommand

from datetime import datetime,timedelta
import os
from sqlalchemy.orm import sessionmaker
from .models import User
import json
import jwt
from functools import wraps


'''
NOTE:
Use jsonify function to return the outputs and status code

Example:
with output
return jsonify(output),2000

only status code
return '',404


'''



# Use this token_required method for your routes where ever needed.
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
		if not token:
			return jsonify({'Message':' Token is missing'}), 401
		try:
			print("yes")
			data = jwt.decode(token, app.config['SECRET_KEY'],  algorithms='HS256')
			print(data)
			current_user = User.query.filter_by(user_id=data['id']).first()
			print(current_user.user_id)
			print(current_user.user_role)
		except:
			return jsonify({'Message': 'Token is invalid'}), 401
		return f(current_user, *args, **kwargs)
	return decorated


	
#Write your code here for the API end points





