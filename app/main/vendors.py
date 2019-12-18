from flask import redirect, jsonify, request
from app.main import application
from flask_login import login_required
from app.data.models.items import Items
from app.data.models.vendors import Vendors
from app import db
import json
import urllib.request
from urllib.error import HTTPError
from werkzeug.urls import url_parse
import requests


@application.route('/vendorModal/<item_id>', methods= ['GET','POST'])
def vendorModal(item_id):
    item = Items.query.get(item_id)
    uri = "http://gimel.compbio.ucsf.edu:5022/api/_new_get_data?molecule_id=" + item.identifier+'&source_database=' + item.database
    req = urllib.request.Request(url=uri,headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
    try:
        with urllib.request.urlopen(req) as url:
            data = json.loads(url.read().decode())
            priceAPI = []
            for d in data:
                priceAPI.append(d)
            for i in priceAPI:
                for pack in i['packs']:
                    vendor = Vendors.query.filter_by(item_fk=item_id, cat_id_fk=i['cat_id_fk'], supplier_code=i['supplier_code'], pack_quantity=pack['quantity'], unit=pack['unit']).first()
                    if vendor:
                            pack['purchase_quantity'] = vendor.purchase_quantity
                            pack['class']="success"
                    else:
                        pack['purchase_quantity'] = 0
                        pack['class']=""
            return jsonify(priceAPI)
    except HTTPError as e:
        content = e.read()
        return jsonify('null')

@application.route('/vendorUpdate', methods= ['POST'])
def vendorUpdate():
    data = request.get_json()
    # Since user chose new vendors we do not need to store old chosen vendors
    Vendors.query.filter_by(item_fk = data['item_id']).delete()
    for item in data['post_data']:
        Vendors.createVendor(item, data['item_id'])
    return jsonify('success')