from flask import jsonify, request, render_template, url_for
from app.main import application
from flask_login import current_user
from flask_login import login_required
from app.data.models.carts import Carts
from app.data.models.items import Items
from app.data.models.items import Vendors
# from app.main.vendors import getVendors
import json


@application.route('/addToCart', methods=['POST'])
# adding Item to Cart
def addToCart():
    activeCart = Carts.query.get(current_user.activeCart)
    data = request.get_json()
    item_id = activeCart.addToCart(current_user, data['id'], data['img_url'], data['database'])
    print(item_id)
    if item_id:
        count = current_user.cart_count
        return jsonify({'count': current_user.cart_count, 'item_id': item_id})
    return jsonify({'count': current_user.cart_count, 'item_id': item_id})


@application.route('/addToCartWithVendor', methods=['POST'])
# adding Item to Cart
def addToCartWithVendor(identifier, img, db, vendor) -> None:
    print("calling addToCartWithVendor")
    if current_user.is_authenticated:
        activeCart = Carts.query.get(current_user.activeCart)
        item_id = activeCart.addToCartGetId(current_user, identifier, img, db)
        if vendor:
            vendor_ = Vendors.addVendor(item_id, vendor)
        print('added succeesfully')
    return 'success'
    # return 'sucess'
    # data = request.get_json()
    # item_id = activeCart.addToCart(current_user, data['id'],data['img_url'],data['database'])
    # print(item_id)
    # if item_id:
    #     count = current_user.cart_count
    #     return jsonify({'count':current_user.cart_count, 'item_id':item_id})    
    # return jsonify({'count':current_user.cart_count, 'item_id':item_id})


@application.route('/deleteItem/<identifier>', methods=['DELETE'])
def deleteItem(identifier):
    Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first().deleteItem()
    print(identifier)
    items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
    print(items)
    print(len(items))
    return jsonify({'count': current_user.cart_count})


@application.route('/showItem')
def showItem():
    data = json.loads(request.args.get('data'))
    return render_template('cart/item.html', identifier=data['identifier'], img=data['img'], db=data['db'])


@application.route("/processItem", methods=['POST'])
def processItem():
    data = request.get_json()
    return jsonify({
        'result': url_for('main.showItem',
                          data=json.dumps({"identifier": data['identifier'], "img": data['img'], "db": data['db']}))
    })
