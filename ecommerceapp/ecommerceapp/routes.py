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
from .models import *
import base64

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

@app.route('/api/public/login')
def login():
    value = request.headers.get("Authorization") # 'Basic token'
    username, password = base64.b64decode(value.split(' ')[1]).decode('UTF-8').split(':') # 'apple:pass_word'
    print(username)
    print(password)
    user = User.query.filter_by(user_name = username).first()

    if user:
        if check_password_hash(user.password, password):
            token = jwt.encode({
            'id': user.user_id
        }, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify(token = token), 200 # OK
    return '', 401 # unauthorized


@app.route('/api/public/product/search', methods=['GET'])
def product():
    args = request.args
    products = db.session.query(Product, Category).join(Category).filter(Product.product_name == args.get("keyword")).all()
    res = []
    if not products:
        return '', 400 # Bad Request
    for product, category in products:
        res.append({"category": {"category_id": category.category_id, "category_name": category.category_name}, "price": product.price, "product_name": product.product_name, "product_id": product.product_id, "seller_id": product.seller_id})
    
    return jsonify(res)


@app.route('/api/auth/consumer/cart', methods=['GET'])
@token_required
def cart_detail(current_user):
    total_detail = db.session.query(Cart, CartProduct, Product, Category).select_from(Cart).join(CartProduct).join(Product).join(Category).filter(Cart.user_id == current_user.user_id).all()
    print(total_detail)
    res = []
    if not total_detail:
          return '', 403 # forbidden
    
    for cart, cart_product, product, cateogry in total_detail:
        res.append({
            "cartproducts": {
                "product": {
                    "product_id": product.product_id,
                    "price": product.price,
                    "product_name": product.product_name,
                    "category": {
                        "category_name": cateogry.category_name,
                        "category_id": cateogry.category_id
                    }
                },
                "cp_id": cart_product.cp_id,
            },
            "cart_id": cart.cart_id,
            "total_amount": cart.total_amount
        })
    return jsonify(res), 200

@app.route('/api/auth/consumer/cart', methods=['POST', 'PUT', 'DELETE'])
@token_required
def update_cart_detail(current_user):
	if request.method == 'DELETE':
		product_id = request.json['product_id']
	else:
		product_id = request.json['product_id']
		quantity = request.json['quantity']
	cart = Cart.query.filter_by(user_id = current_user.user_id).first()
	product = Product.query.filter_by(product_id = product_id).first()
	if not cart or not product:
		return '', 403
	cart_product = CartProduct.query.filter_by(product_id = product_id).first()
	if request.method == 'POST':
		if cart_product:
			return '', 409
		else:
			cart_product = CartProduct(
				cart_id = cart.cart_id,
				product_id = product_id,
				quantity = quantity
			)
			cart.total_amount += quantity * product.price
	if request.method == 'PUT':
		if cart_product:
			cart.total_amount = cart.total_amount - cart_product.quantity * product.price + quantity * product.price
			cart_product.quantity = quantity
	if request.method == 'POST' or request.method == 'PUT':
		db.session.add(cart_product)
	else:
		cart.total_amount -= cart_product.quantity * product.price
		db.session.delete(cart_product)
	db.session.add(cart)
	db.session.commit()
	return str(cart.total_amount), 200


@app.route('/api/auth/seller/product', methods=['GET'])
@token_required
def get_products(current_user):
	products = db.session.query(User, Product, Category).select_from(User).join(Product).join(Category).filter(User.user_id == current_user.user_id).all()
	if not products:
		return '', 403
	res = []
	for user, product, category in products:
		res.append({
				"category": {
				"category_id": category.category_id,
				"category_name": category.category_name
			},
			"price": product.price,
			"product_id": product.product_id,
			"product_name": product.product_name,
			"seller_id": product.seller_id
		})
	return jsonify(res), 200


@app.route('/api/auth/seller/product/<int:product_id>', methods=['GET', 'DELETE'])
@token_required
def get_single_product(current_user, product_id):
	if current_user.user_role == 1:
		return '', 403
	products = db.session.query(Product, Category).select_from(User).join(Product).join(Category).filter(User.user_id == current_user.user_id).filter(Product.product_id == product_id).all()
	print(products)
	if not products:
		return '', 404
	
	if request.method == 'DELETE':
		db.session.delete(products[0][0])
		db.session.commit()
		return '', 200

	res = []
	for product, category in products:
		res.append({
				"category": {
				"category_id": category.category_id,
				"category_name": category.category_name
			},
			"price": product.price,
			"product_id": product.product_id,
			"product_name": product.product_name,
			"seller_id": product.seller_id
		})
	return jsonify(res), 200


@app.route('/api/auth/seller/product', methods=['POST', 'PUT'])
@token_required
def add_product(current_user):
	if current_user.user_role == 1:
		return '', 403
	if request.method == 'POST':
		product_id = request.json['product_id']
		product = Product.query.filter_by(product_id = product_id).first()
		if product:
			return '', 409
		product_name = request.json['product_name']
		price = request.json['price']
		category_id = request.json['category_id']

		new_product = Product(
			product_id = product_id,
			product_name = product_name,
			price = price,
			seller_id = current_user.user_id,
			category_id = category_id
		)
		db.session.add(new_product)
		db.session.commit()
		return str(product_id), 201
	if request.method == 'PUT':
		product_id = request.json['product_id']
		product = Product.query.filter(Product.seller_id == current_user.user_id).filter(Product.product_id == product_id).first()

		if product:
			product.price = request.json['price']
		else:
			return '', 404
		
		db.session.add(product)
		db.session.commit()
		return '', 200
