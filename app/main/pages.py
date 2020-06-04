from flask import render_template, request, jsonify, session
from app.main import application
from flask_login import current_user, login_required
from app.data.models.availableVendors import AvailableVendors, UserVendors
from app import db
import json
from app.data.models.users import Users
from app.data.models.carts import Carts

@application.route('/', methods=['GET'])
@application.route('/cartblanche', methods=['GET'])
def cartblanche():
    response = []
    identifiers = []
    is_authenticated = False
    cart_count=0
    punchout = False
    print(session)
    url = ''
    if 'url' in session.keys():
        url = session['url']
        punchout = True
    if current_user.is_authenticated:
        cart = current_user.items_in_cart
        for c in cart:
            identifiers.append(c.identifier)
            item = {}
            item['identifier'] = c.identifier
            item['db'] = c.database
            item['img'] = c.compound_img
            supplier = []
            for v in c.vendors:
                vendor = {}
                vendor['cat_name'] = v.cat_name
                vendor['supplier_code'] = v.supplier_code
                vendor['quantity'] = v.pack_quantity
                vendor['unit'] = v.unit
                vendor['price'] = v.price
                vendor['purchase'] = v.purchase_quantity
                vendor['shipping'] = v.shipping_str
                supplier.append(vendor)
            item['supplier'] = supplier
            response.append(item)
        cart_count=len(cart)
        is_authenticated = True
    return render_template('cartblanche.html', cart=json.dumps(response), items = json.dumps(identifiers), is_authenticated=is_authenticated, cart_count=cart_count, url = url, punchout = punchout)

@application.route('/profile', methods=['GET'])
def profile():
    for i in AvailableVendors.query.all():
        if not UserVendors.query.filter_by(user_id=current_user.id, vendor_id=i.vendor_id).first():
            vendor = UserVendors(user_id=current_user.id, vendor_id=i.vendor_id, priority=i.priority)
            db.session.add(vendor)
            db.session.commit()
    return render_template('profile.html', data=current_user.vendors)

@application.route('/updateVendorPriority', methods=['POST'])
def updateVendorPriority():
    data = request.get_json()
    vendor = UserVendors.query.get(data['id'])
    if int(data['value']) > 100:
        vendor.priority = 100
    elif int(data['value']) < 0:
        vendor.priority = 0
    else:
        vendor.priority = int(data['value'])
    db.session.commit()
    return jsonify({'priority' : vendor.priority})