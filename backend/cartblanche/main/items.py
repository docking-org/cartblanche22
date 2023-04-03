from flask import jsonify, request, render_template, url_for
from cartblanche.app import app 
from flask_login import current_user
from flask_login import login_required
from cartblanche.data.models.carts import Carts
from cartblanche.data.models.items import Items
from cartblanche.data.models.vendors import Vendors
# from app.main.vendors import getVendors
import json
from cartblanche.app import db


@app.route('/addToCart', methods=['POST'])
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


@app.route('/addToCartWithVendor', methods=['POST'])
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


@app.route('/deleteItem/<identifier>', methods=['DELETE'])
def deleteItem(identifier):
    Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first().deleteItem()
    print(identifier)
    items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
    print(items)
    print(len(items))
    return jsonify({'count': current_user.cart_count})


@app.route('/showItem')
def showItem():
    data = json.loads(request.args.get('data'))
    print(data)
    return render_template('cart/item.html', identifier=data['identifier'], img=data['img'], db=data['db'], smile=data['smile'])


@app.route("/processItem", methods=['POST'])
def processItem():
    data = request.get_json()
    print(data)
    return jsonify({
        'result': url_for('main.showItem',
                          data=json.dumps({"identifier": data['identifier'], "img": data['img'], "db": data['db'], "smile":data['smile']}))
    })
