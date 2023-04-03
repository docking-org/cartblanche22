from flask import redirect, jsonify, request, url_for, session, render_template
from cartblanche.app import app 
from cartblanche.data.models.default_prices import DefaultPrices
from flask_login import current_user


@app.route("/getDefaultPrices", methods=['GET'])
def getDefaultPrices():
    org = ''
    if current_user.is_authenticated and current_user.has_roles('ucsf'):
        org = 'ucsf'
    else:
        org = 'public'
    vendor_prices = {}
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
