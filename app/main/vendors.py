from flask import redirect, jsonify, request
from app.main import application
from flask_login import login_required, current_user
from app.data.models.items import Items
from app.data.models.vendors import Vendors
from app.data.models.carts import Carts
from app.data.models.availableVendors import AvailableVendors, UserVendors
from app import db
import json, requests
import urllib.request
from urllib.error import HTTPError
from werkzeug.urls import url_parse
import requests
from collections import OrderedDict 
from operator import getitem
import asyncio
from app.main.items import addToCartWithVendor

@application.route('/updateVendor', methods=['PUT'])
def updateVendor():
    if current_user.is_authenticated:
        activeCart = Carts.query.get(current_user.activeCart)
        data = request.get_json()
        item = Items.query.filter_by(identifier=data['identifier'], cart_fk=current_user.activeCart).first()
        vendor = Vendors.query.filter_by(item_fk=item.item_id, cat_name=data['cat_name'],                   supplier_code=data['supplier_code'], price=float(data['price']),                   pack_quantity=float(data['quantity']), unit=data['unit']).first()
        vendor.updatePurchaseQuantity(data['purchase'])
    return jsonify('successfully updated vendor purchase to db')

@application.route('/addVendor', methods=['POST'])
def addVendor():
    if current_user.is_authenticated:
        activeCart = Carts.query.get(current_user.activeCart)
        data = request.get_json()
        item_id = activeCart.addToCartGetId(current_user, data['identifier'], data['img'], data['db'])
        vendor_ = Vendors.addVendor(item_id, data['vendor'])
        print('added succeesfully')
        print(vendor_)
    return jsonify('successfullt added vendor to db')

@application.route('/deleteVendor', methods=['POST'])
def deleteVendor():
    if current_user.is_authenticated:
        data = request.get_json()
        item = Items.query.filter_by(identifier=data['identifier'], cart_fk=current_user.activeCart).first()
        vendors =  Vendors.query.filter_by(item_fk=item.item_id).all()
        if len(vendors) <= 1:
            item.deleteItem()
        else:            
            vendor = Vendors.query.filter_by(item_fk=item.item_id, cat_name=data['cat_name'],                   supplier_code=data['supplier_code'], price=float(data['price']),                   pack_quantity=float(data['quantity']), unit=data['unit']).first()
            vendor.deleteVendor()
    return jsonify('successfully deleted vendor from db')

@application.route('/vendorsFromZinc', methods=['GET'])
def vendorsFromZinc():
    files = {
    'purchasable-between': '10 50',
    'count': 'all',
    'output_fields': 'cat_id bb short_name purchasable name',
    }
    response = requests.get('https://zinc15.docking.org/catalogs.txt', params=files)
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
    '''used to automatically choose one vendor from vendors. Currently it's taking lowest pack with lowest price'''
    print('autoChoosing Vendor for {}'.format(item_id))
    item = Items.query.get(item_id)
    payload = {'molecule_id' : ''.join(item.identifier.split()), 'source_database' : item.database}
    response = requests.get('https://gimel.compbio.ucsf.edu:5022/api/_new_get_data', params=payload)
    if response and len(response.json()) > 0:
        res = response.json()
        print(res)
        for i in res:
            i['packs'].sort(key = lambda x : (x['price'], x['quantity']))
        res = sorted(res, key = lambda x : x['packs'][0]['price'])
        vendor = {'cat_name' : res[0]['cat_name'], 'cat_id_fk':res[0]['cat_id_fk'], 'purchase_quantity': 1, 'supplier_code':res[0]['supplier_code'], 'price':res[0]['packs'][0]['price'], 'quantity':res[0]['packs'][0]['quantity'], 'unit':res[0]['packs'][0]['unit']}
        Vendors.createVendor(vendor, item_id)
    else:
        return jsonify(success=False, message="Problem causing with price api request or empty")
    return jsonify(success=True)

@application.route('/getVendors/<identifier>/<db>', methods= ['GET'])
def getVendors(identifier, db):
    payload = {'molecule_id' : identifier , 'source_database' : db}
    response = requests.get('http://prices.docking.org/api/_new_get_data', params=payload)
    vendors = []
    if response and len(response.json()) > 0:
        res = response.json()
        i = 0
        for vendor in res:
            for pack in vendor['packs']:
                i+=1
                temp = {}
                temp['cat_name'] = vendor['cat_name']
                temp['supplier_code'] = vendor['supplier_code']
                temp['quantity'] = pack['quantity']
                temp['unit'] = pack['unit']
                temp['price'] = pack['price']
                temp['shipping'] = pack['shipping']
                temp['DT_RowId'] = i
                vendors.append(temp)
    return jsonify({'vendors' : vendors})

@application.route('/chooseVendor', methods= ['GET', 'POST'])
def chooseVendor():
    '''used to automatically choose one vendor from vendors. Currently it's taking lowest pack with lowest price'''
    data = request.get_json()
    print(data)
    assigned = True
    payload = {'molecule_id' : data['identifier'], 'source_database' : data['db']}
    response = requests.get('http://prices.docking.org/api/_new_get_data', params=payload)
    if response and len(response.json()) > 0:
        res = response.json()
        print(res)
        for i in res:
            i['packs'].sort(key = lambda x : (x['price'], x['quantity']))
        res = sorted(res, key = lambda x : x['packs'][0]['price'])
        vendor = {'cat_name' : res[0]['cat_name'], 'cat_id_fk':res[0]['cat_id_fk'], 'purchase': 1, 'supplier_code':res[0]['supplier_code'], 'price':res[0]['packs'][0]['price'], 'quantity':res[0]['packs'][0]['quantity'], 'unit':res[0]['packs'][0]['unit'],'shipping':res[0]['packs'][0]['shipping']}
    else:
        assigned = False
        vendor={}
    addToCartWithVendor(data['identifier'], data['img'], data['db'], vendor)
    return jsonify({'vendor':vendor, 'assigned' : assigned})

@application.route('/vendorModal/<item_id>', methods= ['GET','POST'])
def vendorModal(item_id):
    item = Items.query.get(item_id)
    payload = {'molecule_id' : ''.join(item.identifier.split()), 'source_database' : item.database}
    response = requests.get('http://gimel.compbio.ucsf.edu:5022/api/_new_get_data', params=payload)
    if response:
        data = response.json()
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
    else:
        jsonify('null')

@application.route('/vendorUpdate', methods= ['GET', 'POST'])
def vendorUpdate():
    data = request.get_json()
    # Since user chose new vendors we do not need to store old chosen vendors
    Vendors.query.filter_by(item_fk = data['item_id']).delete()
    for item in data['post_data']:
        Vendors.createVendor(item, data['item_id'])
    return jsonify('success')

@application.route('/getVendorDummy')
def getVendorDummy():
    return jsonify([{"supplier_code": "W-100283", "cat_name": "Biosynth AG", "cat_id_fk": 85, "molecule_id": "ZINC000100074375", "cs_id": "CSC000185809", "packs": [{"price": 190, "currency": "USD", "quantity": 5, "unit": "g", "shipping": "28 days"}]}, {"supplier_code": "CUS57303359", "cat_name": "Curpys Chemicals", "cat_id_fk": 85, "molecule_id": "ZINC000100074375", "cs_id": "CSC000185809", "packs": [{"price": 27, "currency": "USD", "quantity": 0.001, "unit": "g", "shipping": "7 days"}, {"price": 31, "currency": "USD", "quantity": 0.002, "unit": "g", "shipping": "7 days"}, {"price": 44, "currency": "USD", "quantity": 0.005, "unit": "g", "shipping": "7 days"}, {"price": 53, "currency": "USD", "quantity": 0.01, "unit": "g", "shipping": "7 days"}, {"price": 73, "currency": "USD", "quantity": 0.02, "unit": "g", "shipping": "7 days"}]}, {"supplier_code": "EN300-18009", "cat_name": "Enamine Ltd", "cat_id_fk": 85, "molecule_id": "ZINC000100074375", "cs_id": "CSC000185809", "packs": [{"price": 19, "currency": "USD", "quantity": 1, "unit": "g", "shipping": "2 days"}, {"price": 20, "currency": "USD", "quantity": 2.5, "unit": "g", "shipping": "2 days"}, {"price": 21, "currency": "USD", "quantity": 5, "unit": "g", "shipping": "2 days"}, {"price": 22, "currency": "USD", "quantity": 10, "unit": "g", "shipping": "2 days"}]}, {"supplier_code": "Amb22232205", "query_molecule": "ZINC000100074375", "cat_id_fk": 111, "cat_name": "Ambinter", "packs": [{"price": 300.0, "currency": "USD", "quantity": 10.0, "unit": "mg", "shipping": "On Demand"}]}, {"supplier_code": "Z57127482", "query_molecule": "ZINC000100074375", "cat_id_fk": 184, "cat_name": "Enamine-REAL", "packs": [{"price": 100.0, "currency": "USD", "quantity": 10.0, "unit": "mg", "shipping": "On Demand"}]}, {"supplier_code": "BBV-76025089", "query_molecule": "ZINC000100074375", "cat_id_fk": 333, "cat_name": "Enamine BB make-on-demand", "packs": [{"price": 250.0, "currency": "USD", "quantity": 250.0, "unit": "mg", "shipping": "On Demand"}]}, {"cat_name": "Otava, Ltd.", "cat_id_fk": 385, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "2829786", "packs": [{"price": 24.9, "currency": "USD", "quantity": 1, "unit": "mg", "shipping": "10 days"}, {"price": 28.0, "currency": "USD", "quantity": 2, "unit": "mg", "shipping": "10 days"}, {"price": 31.0, "currency": "USD", "quantity": 3, "unit": "mg", "shipping": "10 days"}, {"price": 33.0, "currency": "USD", "quantity": 4, "unit": "mg", "shipping": "10 days"}, {"price": 40.0, "currency": "USD", "quantity": 5, "unit": "mg", "shipping": "10 days"}, {"price": 48.0, "currency": "USD", "quantity": 10, "unit": "mg", "shipping": "10 days"}, {"price": 57.0, "currency": "USD", "quantity": 15, "unit": "mg", "shipping": "10 days"}, {"price": 66.0, "currency": "USD", "quantity": 20, "unit": "mg", "shipping": "10 days"}, {"price": 73.0, "currency": "USD", "quantity": 25, "unit": "mg", "shipping": "10 days"}, {"price": 24.9, "currency": "USD", "quantity": 3, "unit": "micromol", "shipping": "10 days"}, {"price": 31.0, "currency": "USD", "quantity": 5, "unit": "micromol", "shipping": "10 days"}, {"price": 40.0, "currency": "USD", "quantity": 10, "unit": "micromol", "shipping": "10 days"}, {"price": 48.0, "currency": "USD", "quantity": 20, "unit": "micromol", "shipping": "10 days"}]}, {"cat_name": "Otava, Ltd. (made-to-order)", "cat_id_fk": 899, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "2829786", "packs": [{"price": 290.0, "currency": "USD", "quantity": 4, "unit": "mg", "shipping": "40 days"}, {"price": 390.0, "currency": "USD", "quantity": 50, "unit": "mg", "shipping": "40 days"}]}, {"cat_name": "ENAMINE Ltd.", "cat_id_fk": 548, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "EN300-18009", "packs": [{"price": 19.0, "currency": "USD", "quantity": 100, "unit": "mg", "shipping": "10 days"}, {"price": 19.0, "currency": "USD", "quantity": 250, "unit": "mg", "shipping": "10 days"}, {"price": 19.0, "currency": "USD", "quantity": 500, "unit": "mg", "shipping": "10 days"}, {"price": 19.0, "currency": "USD", "quantity": 1, "unit": "g", "shipping": "10 days"}, {"price": 20.0, "currency": "USD", "quantity": 2.5, "unit": "g", "shipping": "10 days"}, {"price": 21.0, "currency": "USD", "quantity": 5, "unit": "g", "shipping": "10 days"}, {"price": 22.0, "currency": "USD", "quantity": 10, "unit": "g", "shipping": "10 days"}]}, {"cat_name": "AK Scientific, Inc.", "cat_id_fk": 548, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "G406", "packs": [{"price": 14.0, "currency": "USD", "quantity": 25, "unit": "g", "shipping": "2 days"}, {"price": 27.0, "currency": "USD", "quantity": 100, "unit": "g", "shipping": "2 days"}, {"price": 54.0, "currency": "USD", "quantity": 500, "unit": "g", "shipping": "2 days"}]}, {"cat_name": "AA BLOCKS", "cat_id_fk": 548, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "AA0039G5", "packs": [{"price": 31.0, "currency": "USD", "quantity": 25, "unit": "g", "shipping": "7 days"}, {"price": 45.0, "currency": "USD", "quantity": 100, "unit": "g", "shipping": "7 days"}, {"price": 75.0, "currency": "USD", "quantity": 500, "unit": "g", "shipping": "7 days"}]}, {"supplier_code": "481835", "query_molecule": "ZINC000100074375", "cat_id_fk": 405, "cat_name": "eMolecules", "packs": [{"price": 100.0, "currency": "USD", "quantity": 10.0, "unit": "mg", "shipping": "On Demand"}]}, {"cat_name": "Otava, Ltd.", "cat_id_fk": 385, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "2829786", "packs": [{"price": 24.9, "currency": "USD", "quantity": 1, "unit": "mg", "shipping": "10 days"}, {"price": 28.0, "currency": "USD", "quantity": 2, "unit": "mg", "shipping": "10 days"}, {"price": 31.0, "currency": "USD", "quantity": 3, "unit": "mg", "shipping": "10 days"}, {"price": 33.0, "currency": "USD", "quantity": 4, "unit": "mg", "shipping": "10 days"}, {"price": 40.0, "currency": "USD", "quantity": 5, "unit": "mg", "shipping": "10 days"}, {"price": 48.0, "currency": "USD", "quantity": 10, "unit": "mg", "shipping": "10 days"}, {"price": 57.0, "currency": "USD", "quantity": 15, "unit": "mg", "shipping": "10 days"}, {"price": 66.0, "currency": "USD", "quantity": 20, "unit": "mg", "shipping": "10 days"}, {"price": 73.0, "currency": "USD", "quantity": 25, "unit": "mg", "shipping": "10 days"}, {"price": 24.9, "currency": "USD", "quantity": 3, "unit": "micromol", "shipping": "10 days"}, {"price": 31.0, "currency": "USD", "quantity": 5, "unit": "micromol", "shipping": "10 days"}, {"price": 40.0, "currency": "USD", "quantity": 10, "unit": "micromol", "shipping": "10 days"}, {"price": 48.0, "currency": "USD", "quantity": 20, "unit": "micromol", "shipping": "10 days"}]}, {"cat_name": "Otava, Ltd. (made-to-order)", "cat_id_fk": 899, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "2829786", "packs": [{"price": 290.0, "currency": "USD", "quantity": 4, "unit": "mg", "shipping": "40 days"}, {"price": 390.0, "currency": "USD", "quantity": 50, "unit": "mg", "shipping": "40 days"}]}, {"cat_name": "ENAMINE Ltd.", "cat_id_fk": 548, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "EN300-18009", "packs": [{"price": 19.0, "currency": "USD", "quantity": 100, "unit": "mg", "shipping": "10 days"}, {"price": 19.0, "currency": "USD", "quantity": 250, "unit": "mg", "shipping": "10 days"}, {"price": 19.0, "currency": "USD", "quantity": 500, "unit": "mg", "shipping": "10 days"}, {"price": 19.0, "currency": "USD", "quantity": 1, "unit": "g", "shipping": "10 days"}, {"price": 20.0, "currency": "USD", "quantity": 2.5, "unit": "g", "shipping": "10 days"}, {"price": 21.0, "currency": "USD", "quantity": 5, "unit": "g", "shipping": "10 days"}, {"price": 22.0, "currency": "USD", "quantity": 10, "unit": "g", "shipping": "10 days"}]}, {"cat_name": "AK Scientific, Inc.", "cat_id_fk": 548, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "G406", "packs": [{"price": 14.0, "currency": "USD", "quantity": 25, "unit": "g", "shipping": "2 days"}, {"price": 27.0, "currency": "USD", "quantity": 100, "unit": "g", "shipping": "2 days"}, {"price": 54.0, "currency": "USD", "quantity": 500, "unit": "g", "shipping": "2 days"}]}, {"cat_name": "AA BLOCKS", "cat_id_fk": 548, "molecule_id": "ZINC000100074375", "molport_id": "MolPort-001-738-537", "supplier_code": "AA0039G5", "packs": [{"price": 31.0, "currency": "USD", "quantity": 25, "unit": "g", "shipping": "7 days"}, {"price": 45.0, "currency": "USD", "quantity": 100, "unit": "g", "shipping": "7 days"}, {"price": 75.0, "currency": "USD", "quantity": 500, "unit": "g", "shipping": "7 days"}]}])