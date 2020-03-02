from flask import jsonify, request
from app.main import application
from flask_login import current_user
from flask_login import login_required
from app.data.models.carts import Carts
from app.data.models.items import Items
from app.data.models.items import Vendors
import json
import urllib.request
from urllib.error import HTTPError
from werkzeug.urls import url_parse

@application.route('/addToCart', methods= ['POST'])
# adding Item to Cart
def addToCart():
    activeCart = Carts.query.get(current_user.activeCart)
    data = request.get_json()
    item_id = activeCart.addToCart(current_user, data['id'],data['img_url'],data['database'])
    if item_id:
        count = current_user.cart_count
        return jsonify({'count':current_user.cart_count, 'item_id':item_id})    
    return jsonify({'count':current_user.cart_count, 'item_id':item_id})

@application.route('/deleteItem/<identifier>', methods= ['DELETE'])
def deleteItem(identifier):
    Items.query.filter_by(identifier=identifier).first().deleteItem()
    return jsonify({'count':current_user.cart_count})