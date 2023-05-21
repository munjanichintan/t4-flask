from ecommerceapp import app, db
from ecommerceapp.models import User, Product, Category, CartProduct, Cart
from flask import request, jsonify, make_response
import base64
from werkzeug.security import check_password_hash, generate_password_hash
from flask_marshmallow import Marshmallow

ma = Marshmallow(app)

# @app.route('/api/public/login')
# def login():

#     value = request.headers.get("Authorization") # 'Basic token'
#     username, password = base64.b64decode(value.split(' ')).decode('UTF-8').split(':') # 'apple:pass_word'

#     user = User.query.filter_by(user_name = username).first()

#     if user:
#         if check_password_hash(user.password, password):
#             token = jwt.encode({''}, algorithm='HS256')
#             return jsonify(token = token), 200
#     return '', 401

@app.route('/api/public/product/search', methods=['GET'])
def product():
    args = request.args
    products = db.session.query(Product, Category).join(Product, Product.category_id == Category.category_id).filter(Product.product_name == args.get("keyword")).all()
    res = []
    if not products:
        return '', 400
    for product, category in products:
        res.append({"category": {"category_id": category.category_id, "category_name": category.category_name}, "price": product.price, "product_name": product.product_name, "product_id": product.product_id, "seller_id": product.seller_id})
    
    return jsonify(res)
    

# class ProductSchema(ma.Schema):
#     class Meta:
#         fields = ('price', 'product_id', 'product_name', 'seller_id')

# class CategorySchema(ma.Schema):
#     class Meta:
#         fields = ('category_id', 'category_name')

# product_schema = ProductSchema()
# category_schema = CategorySchema()



@app.route('/api/public/total', methods=['GET'])
def total():
    args = request.args
    total_detail = db.session.query(Cart, User, CartProduct, Product, Category).select_from(User).join(Cart).join(CartProduct).join(Product).join(Category).filter(User.user_id == args.get("user_id")).all()

    print(total_detail)
    res = []
    for cart, user, cart_product, product, cateogry in total_detail:
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