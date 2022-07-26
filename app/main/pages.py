from flask import render_template, request, jsonify, session
from app.main import application
from flask_login import current_user
from app.data.models.availableVendors import AvailableVendors, UserVendors
from app.data.models.default_prices import DefaultPrices
from app import db
import json


@application.route('/', methods=['GET'])
@application.route('/cartblanche', methods=['GET'])
def cartblanche():
    punchout = False
    checkCart = False
    url = ''
    if 'url' in session.keys():
        url = session['url']
        punchout = True
    if current_user.is_authenticated:
        if 'checkCart' in session.keys():
            checkCart = session['checkCart']
            session['checkCart'] = False
    return render_template('cartblanche.html',
                           is_authenticated=current_user.is_authenticated, url=url, punchout=punchout,
                           loadCartFromDb=checkCart)


@application.route('/profile', methods=['GET'])
def profile():
    for i in AvailableVendors.query.all():
        if not UserVendors.query.filter_by(user_id=current_user.id, vendor_id=i.vendor_id).first():
            vendor = UserVendors(user_id=current_user.id, vendor_id=i.vendor_id, priority=i.priority)
            db.session.add(vendor)
            db.session.commit()
    return render_template('profile.html', data=current_user.vendors)


@application.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


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


@application.route('/loadApplication')
def loadApplication():
    vendor_prices = {}
    org = 'public'
    if current_user.is_authenticated and current_user.has_roles('ucsf'):
        org = 'ucsf'
    default_prices = DefaultPrices.query.filter_by(organization=org).all()
    for d in default_prices:
        vendor = {}
        vendor['cat_name'] = d.category_name
        vendor['supplier_code'] = d.category_name
        vendor['quantity'] = d.quantity
        vendor['unit'] = d.unit
        vendor['price'] = d.price
        vendor['shipping'] = d.shipping
        vendor['organization'] = d.organization
        vendor['assigned'] = False
        vendor['purchase'] = 1
        vendor_prices[d.short_name] = vendor
    return jsonify(vendor_prices)