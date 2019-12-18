from flask import render_template, flash, redirect, url_for, jsonify, request
from app.main import application
from flask_login import current_user
from app.data.models.carts import Carts
from app.data.models.items import Items


@application.route('/cart', methods= ['GET',  'POST'])
def cart():
    items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
    totalPrices=[]
    totalQuantities=[]
    return render_template('cart/cart.html', data=items, prices=totalPrices, quantities=totalQuantities)

@application.route('/carts', methods= ['GET',  'POST'])
def carts():
    carts = Carts.query.filter_by(user_fk=current_user.id).all()
    return render_template('cart/cartlist.html', carts=carts)

@application.route('/createCart', methods= ['GET'])
def createCart():
    Carts.createCart(current_user)
    return redirect(url_for('main.carts'))

@application.route('/renameCart', methods= ['POST'])
def renameCart():
    data = request.get_json()
    Carts.query.get(data['cart_id']).setName(data['name'])
    return jsonify('Cart name successfully updated')

@application.route('/deleteCart/<cart_id>', methods= ['DELETE'])
def deleteCart(cart_id):
    Carts.query.get(cart_id).deleteCart()
    print('cart deleted')
    return jsonify('success')

@application.route('/activateCart/<cart_id>', methods= ['GET'])
def activateCart(cart_id):
    current_user.setCart(cart_id)
    return redirect(url_for('main.carts'))