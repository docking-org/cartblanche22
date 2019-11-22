from flask import jsonify, request
from app.main import application
from flask_login import current_user
from flask_login import login_required
from app.data.models.carts import Carts
from app.data.models.items import Items
import json

@application.route('/addToCart', methods= ['POST'])
# adding Item to Cart
def addToCart():
    activeCart = Carts.query.get(current_user.activeCart)
    data = request.get_json()
    print(data)
    if activeCart.addToCart(current_user, data['id'],data['img_url'],data['database']):
        return jsonify("added to cart")
    return jsonify("item existed in cart")

@application.route('/deleteItem/<identifier>', methods= ['DELETE'])
def deleteItem(identifier):
    Items.query.filter_by(identifier=identifier).first().deleteItem()
    return jsonify("success")