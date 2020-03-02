from flask import redirect, jsonify, request
from app.main import application
from flask_login import login_required, current_user
from app.data.models.items import Items
from app.data.models.vendors import Vendors
from app.data.models.availableVendors import AvailableVendors, UserVendors
from app import db
import json
import urllib.request
from urllib.error import HTTPError
from werkzeug.urls import url_parse
import requests
from collections import OrderedDict 
from operator import getitem


@application.route('/vendorsFromZinc', methods=['GET'])
def vendorsFromZinc():
    files = {
    'purchasable-between': '10 50',
    'count': 'all',
    'output_fields': 'cat_id bb short_name purchasable name',
    }
    response = requests.get('http://zinc15.docking.org/catalogs.txt', params=files)
    if response:
        AvailableVendors.query.update({AvailableVendors.availability:False})
        db.session.commit()
        for line in response.text.split('\n'):
            l = line.split('\t')
            if len(l) == 5:
                if l[1] == "True":
                    l[1] = True
                else:
                    l[1] = False
                if AvailableVendors.query.filter_by(cat_id_fk=l[0], short_name=l[2]).first():
                    AvailableVendors.query.filter_by(cat_id_fk=l[0], short_name=l[2]).first().availability = True
                    db.session.commit()
                else:
                    AvailableVendors.createAvailableVendors(l)
    return

@application.route('/autoChooseVendor/<item_id>', methods= ['POST'])
def autoChooseVendor(item_id):
    print("comes here")
    print(item_id)
    item = Items.query.get(item_id)
    uri = "http://gimel.compbio.ucsf.edu:5022/api/_new_get_data?molecule_id=" +item.identifier+'&source_database=' + item.database
    req = urllib.request.Request(url=uri,headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
    try:
        with urllib.request.urlopen(req) as url:
            res = json.loads(url.read().decode())
            print(res)
            for i in res:
                i['packs'].sort(key = lambda x : (x['price'], x['quantity']))
            res = sorted(res, key = lambda x : x['packs'][0]['price'])
            vendor = {'cat_name' : res[0]['cat_name'], 'cat_id_fk':res[0]['cat_id_fk'], 'purchase_quantity': 1, 'supplier_code':res[0]['supplier_code'], 'price':res[0]['packs'][0]['price'], 'quantity':res[0]['packs'][0]['quantity'], 'unit':res[0]['packs'][0]['unit']}
            Vendors.createVendor(vendor, item_id)
    except HTTPError as e:
        pass
    return jsonify("chosen")

@application.route('/vendorModal/<item_id>', methods= ['GET','POST'])
def vendorModal(item_id):
    item = Items.query.get(item_id)
    id = ''.join(item.identifier.split())
    uri = "http://gimel.compbio.ucsf.edu:5022/api/_new_get_data?molecule_id=" + id+'&source_database=' + item.database
    print(uri)
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