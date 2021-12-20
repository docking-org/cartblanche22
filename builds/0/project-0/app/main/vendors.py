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
from app.data.models.default_prices import DefaultPrices


@application.route('/getVendor', methods=['POST'])
def getVendor():
    supplier = request.get_json()['data']
    print(supplier.split(','))
    if current_user.is_authenticated and current_user.has_roles('ucsf'):
        role = 'ucsf'
    else:
        role = 'public'
    vendor = {}
    vendor['catalog_name'] = None
    vendor['quantity'] = None
    vendor['unit'] = None
    vendor['price'] = float('inf')
    vendor['shipping'] = None
    vendor['supplier_code'] = None
    for s in supplier:
        price = None
        if 'mcule' in s.lower():
            price = DefaultPrices.query.filter_by(category_name='mcule', organization=role).first()
        elif 'w' in s.lower():
            price = DefaultPrices.query.filter_by(category_name='wuxi', organization=role).first()
        elif 's' in s.lower():
            price = DefaultPrices.query.filter_by(category_name='Enamine_S', organization=role).first()
        else:
            price = DefaultPrices.query.filter_by(category_name='Enamine_M', organization=role).first()
        if price.price < vendor['price']:
            vendor['catalog_name'] = price.category_name
            vendor['quantity'] = price.quantity
            vendor['unit'] = price.unit
            vendor['price'] = price.price
            vendor['shipping'] = price.shipping
            vendor['supplier_code'] = s
    return jsonify(vendor)

@application.route('/vendorsFromZinc', methods=['GET'])
def vendorsFromZinc():
    files = {
        'purchasable-between': '10 50',
        'count': 'all',
        'output_fields': 'cat_id bb short_name purchasable name',
    }
    response = requests.get('https://zinc15.docking.org/catalogs.txt', params=files)
    if response:
        AvailableVendors.query.update({AvailableVendors.availability: False})
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


@application.route('/autoChooseVendor/<item_id>', methods=['POST'])
def autoChooseVendor(item_id):
    '''used to automatically choose one vendor from vendors. Currently it's taking lowest pack with lowest price'''
    print('autoChoosing Vendor for {}'.format(item_id))
    item = Items.query.get(item_id)
    payload = {'molecule_id': ''.join(item.identifier.split()), 'source_database': item.database}
    # response = requests.get('http://ec2-52-53-226-228.us-west-1.compute.amazonaws.com/api/_new_get_data',
    #                         params=payload)
    response = requests.get('https://prices.docking.org/api/_new_get_data', params=payload)
    if response and len(response.json()) > 0:
        res = response.json()
        print(res)
        for i in res:
            i['packs'].sort(key=lambda x: (x['price'], x['quantity']))
        res = sorted(res, key=lambda x: x['packs'][0]['price'])
        vendor = {'cat_name': res[0]['cat_name'], 'cat_id_fk': res[0]['cat_id_fk'], 'purchase_quantity': 1,
                  'supplier_code': res[0]['supplier_code'], 'price': res[0]['packs'][0]['price'],
                  'quantity': res[0]['packs'][0]['quantity'], 'unit': res[0]['packs'][0]['unit']}
        Vendors.createVendor(vendor, item_id)
    else:
        return jsonify(success=False, message="Problem causing with price api request or empty")
    return jsonify(success=True)


@application.route('/getVendors/<identifier>/<db>', methods=['GET'])
def getVendors(identifier, db):
    payload = {'molecule_id': identifier, 'source_database': db}
    # response = requests.get('http://ec2-54-177-191-93.us-west-1.compute.amazonaws.com/api/_new_get_data',
    #                         params=payload)
    response = requests.get('https://prices.docking.org/api/_new_get_data', params=payload)
    vendors = []
    # print(payload)
    # print(response)
    # print(response.json())
    if response and len(response.json()) > 0:
        res = response.json()
        i = 0
        # print('res', res)
        for vendor in res:
            for pack in vendor['packs']:
                i += 1
                temp = {}
                temp['cat_name'] = vendor['cat_name']
                temp['supplier_code'] = vendor['supplier_code']
                temp['quantity'] = pack['quantity']
                temp['unit'] = pack['unit']
                temp['price'] = pack['price']
                temp['shipping'] = pack['shipping']
                temp['DT_RowId'] = i
                vendors.append(temp)

    return jsonify({'vendors': vendors})


@application.route('/chooseVendor', methods=['GET', 'POST'])
def chooseVendor():
    """USED"""
    """chooseVendor called after adding molecule to the cart"""
    """used to automatically choose one vendor from vendors. Currently it's taking lowest pack with lowest price"""
    data = request.get_json()
    print(data)
    assigned = True
    if data['hg'] == True:
        vendor = {'cat_name': 'HG', 'cat_id_fk': 0, 'purchase': 1,
                  'supplier_code': 'HG', 'price': 0,
                  'quantity': 10, 'unit': 'mg',
                  'shipping': 0}
    else:
        payload = {'molecule_id': data['identifier'], 'source_database': data['db']}
        response = requests.get('https://prices.docking.org/api/_new_get_data', params=payload)
        # response = requests.get('http://ec2-54-177-191-93.us-west-1.compute.amazonaws.com/api/_new_get_data',
        #                         params=payload)

        if response and len(response.json()) > 0:
            res = response.json()
            print(res)
            for i in res:
                i['packs'].sort(key=lambda x: (x['price'], x['quantity']))
            res = sorted(res, key=lambda x: x['packs'][0]['price'])
            vendor = {'cat_name': res[0]['cat_name'], 'cat_id_fk': res[0]['cat_id_fk'], 'purchase': 1,
                      'supplier_code': res[0]['supplier_code'], 'price': res[0]['packs'][0]['price'],
                      'quantity': res[0]['packs'][0]['quantity'], 'unit': res[0]['packs'][0]['unit'],
                      'shipping': res[0]['packs'][0]['shipping']}
        else:
            print('vendor not found')
            assigned = False
            vendor = {}
    addToCartWithVendor(data['identifier'], data['img'], data['db'], vendor)
    return jsonify({'vendor': vendor, 'assigned': assigned})


@application.route('/vendorModal/<item_id>', methods=['GET', 'POST'])
def vendorModal(item_id):
    item = Items.query.get(item_id)
    payload = {'molecule_id': ''.join(item.identifier.split()), 'source_database': item.database}
    response = requests.get('https://prices.docking.org/api/_new_get_data', params=payload)
    # response = requests.get('http://ec2-54-177-191-93.us-west-1.compute.amazonaws.com/api/_new_get_data',
    #                         params=payload)

    if response:
        data = response.json()
        priceAPI = []
        for d in data:
            priceAPI.append(d)
        for i in priceAPI:
            for pack in i['packs']:
                vendor = Vendors.query.filter_by(item_fk=item_id, cat_id_fk=i['cat_id_fk'],
                                                 supplier_code=i['supplier_code'], pack_quantity=pack['quantity'],
                                                 unit=pack['unit']).first()
                if vendor:
                    pack['purchase_quantity'] = vendor.purchase_quantity
                    pack['class'] = "success"
                else:
                    pack['purchase_quantity'] = 0
                    pack['class'] = ""
        return jsonify(priceAPI)
    else:
        jsonify('null')


@application.route('/vendorUpdate', methods=['GET', 'POST'])
def vendorUpdate():
    data = request.get_json()
    # Since user chose new vendors we do not need to store old chosen vendors
    Vendors.query.filter_by(item_fk=data['item_id']).delete()
    for item in data['post_data']:
        Vendors.createVendor(item, data['item_id'])
    return jsonify('success')
