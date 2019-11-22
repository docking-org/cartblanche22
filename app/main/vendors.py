from flask import redirect, jsonify, request
from app.main import application
from flask_login import login_required
from app.data.models.items import Items
from app.data.models.vendors import Vendors
from app import db
import json
import urllib.request
from werkzeug.urls import url_parse
import requests


@application.route('/vendorModal/<item_id>', methods= ['GET','POST'])
def vendorModal(item_id):
    item = Items.query.get(item_id)
    uri = "http://gimel.compbio.ucsf.edu:5022/api/_get_data?molecule_id=" + item.identifier
    with urllib.request.urlopen(uri) as url:
        data = json.loads(url.read().decode())
    if data:
        priceAPI = []
        for d in data:
            priceAPI.append(d)
        for i in priceAPI:
            for pack in i['packs']:
                vendor = Vendors.query.filter_by(item_fk=item_id, cat_id_fk=int(i['cat_id_fk']),
                        pack_quantity=float(pack['quantity']), unit=pack['unit']).first()
                if vendor:
                        pack['purchase_quantity'] = vendor.purchase_quantity
                else:
                    pack['purchase_quantity'] = 0
        return jsonify(priceAPI)
    else:
        return jsonify('null')


@application.route('/vendorUpdate', methods= ['POST'])
def vendorUpdate():
    data = request.get_json()
    # Since user chose new vendors we do not need to store old chosen vendors
    Vendors.query.filter_by(item_fk = data['item_id']).delete()
    for item in data['post_data']:
        Vendors.createVendor(item, data['item_id'])
    return jsonify('success')