import re
import urllib.parse
from flask_login import current_user
from app.data.models.default_prices import DefaultPrices

import gevent.monkey
gevent.monkey.patch_all()

import requests
from app.main import application
from flask import render_template, request, json, jsonify, flash, Markup, abort, redirect
from app.data.models.tin.catalog import CatalogModel
from sqlalchemy.sql.expression import true
from app.data.models.vendors import Vendors
from traceback import print_tb
from unicodedata import category
from gevent import monkey
from app.helpers.validation import get_basic_tranche, get_compound_details
from celery.execute import send_task
from celery.result import AsyncResult
import socket
import grequests
from importlib import reload
reload(socket)


base_url = "https://cartblanche22.docking.org/"
sw_server = 'https://sw.docking.org'
swp_server = 'https://swp.docking.org'
swc_server = 'https://swc.docking.org'


# getting swp view, a section of a hit list, returning JSON for that range.
@application.route('/search/view')
def search_view():
    params = request.query_string.decode("utf-8")
    response = requests.get(swp_server + '/search/view',
                            params=params, auth=('gpcr', 'xtal'))
    return response.json()


@application.route('/search/zincid', methods=["GET", "POST"])
def search_byzincid():
    if request.method == "GET":
        text = Markup('Please contact jjiteam@googlegroups.com with molecules that won\'t look up. '
                      "For more information and updates, <a href=\"https://wiki.docking.org/index.php/Legacy_IDs_in_ZINC22\">check the docking wiki</a>.")

        flash(text)
        return render_template('search/search_byzincid.html')


@application.route('/search/smiles', methods=["GET", "POST"])
def search_bysmiles():
    if request.method == "GET":
        return render_template('search/search_bysmiles.html')


@application.route('/search/catitems', methods=["GET", "POST"])
def search_bysupplier():
    if request.method == "GET":
        text = Markup('Please contact jjiteam@googlegroups.com with molecules that won\'t look up. '
                      "For more information and updates, <a href=\"https://wiki.docking.org/index.php/Legacy_IDs_in_ZINC22\">check the docking wiki</a>.")

        flash(text)
        return render_template('search/search_bysupplier.html')


@application.route('/search/zincid')
def search_zincid():
    return render_template('search/search_byzincid.html')


@application.route('/search/random')
def search_random():
    return render_template('search/search_random.html')


@application.route('/search/catitems')
def search_suppliercode():
    return render_template('search/search_suppliercode.html')


@application.route('/search/smiles')
def search_smiles():
    return render_template('search/search_smiles.html')


@application.route('/search/smiles/vendor')
def search_smiles_vendor():
    return render_template('search/search_smiles_vendor.html')


def is_zinc22(identifier):
    if '-' in identifier:
        return True

    if identifier[0:1].upper() == 'C':
        identifier = identifier.replace('C', 'ZINC')

    if identifier[4:6] == '00':
        return False

    elif identifier.isnumeric():
        return False

    elif identifier[0:4].upper() == 'ZINC':
        if(identifier[4:5].isalnum()):
            return True
        else:
            return False
    else:
        return None


@application.route('/searchZinc/<identifier>')
def searchZinc(identifier):
    return redirect('/substance/'+identifier, code=302)


@application.route('/substance/purchasability/<identifier>', methods=["POST"])
# retrieve the purchasability of a molecule
def search_substance_purchasability(identifier):
    result = {}
    org = 'public'
    if current_user.is_authenticated and current_user.has_roles('ucsf'):
        org = 'ucsf'

    dataset = identify_dataset(identifier)
    price = DefaultPrices.query.filter_by(
        category_name=dataset, organization=org).first()

    # if not part of sw datasets, check if it is a zinc id
    if not price:
        if is_zinc22(identifier):
            data, res, smile, prices, logs = getZincData(identifier)
        else:
            data, res, smile, prices, logs = getZinc20Data(identifier)

        if data:
            data['zinc_id'] = identifier
            data['zinc'] = True
            result = data
        else:
            abort(404)
    else:
        print("hiii")
        result['supplier_code'] = price.category_name
        result['supplier'] = [{
            'assigned': True,
            'cat_name': price.category_name,
            'price': price.price,
            'purchase': 1,
            'quantity': price.quantity,
            'shipping': price.shipping,
            'supplier_code': price.short_name,
            'unit': price.unit
        }]

    return {"data": result}


# a regex to identify the dataset of a molecule
dataset_regex = {
    "Enamine_M": "m_.*|Z[0-9]{9}|PV-[0-9]{12}",
    "Enamine_S": "s_.*",
}


def identify_dataset(identifier):
    for regex in dataset_regex:
        if re.match(dataset_regex[regex], identifier):
            return regex


@application.route('/substance/<identifier>', methods=["GET", "POST"])
def search_substance(identifier):
    if is_zinc22(identifier):
        data, res, smile, prices, logs = getZincData(identifier)
    else:
        data, res, smile, prices, logs = getZinc20Data(identifier)

    if data:
        data['zinc_id'] = identifier

    if request.method == "GET":
        if data:
            return render_template('molecule/mol_index.html', data=data, prices=prices,
                                   smile=urllib.parse.quote(smile), response=res, identifier=identifier, zinc20_stock='zinc20_stock')
        else:
            return render_template('errors/search404.html', lines=data, logs=logs, href='/search/zincid',
                                   header="We didn't find this molecule from Zinc22 database. Click here to return"), 404
    elif request.method == "POST":
        if data:
            return {"data": data}
        else:
            abort(404)


# this is default zinc20 data
def getZinc20Data(identifier):
    zinc20_files = {
        'zinc_id-in': [identifier],
        'output_fields': "zinc_id supplier_code smiles substance_purchasable catalog inchikey"
    }
   
    response = requests.post(
        "https://zinc20.docking.org/catitems/subsets/for-sale.json", data=zinc20_files)
    reload(socket)
    print(response)
    if response:
        role = ''
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            role = 'ucsf'
        else:
            role = 'public'

        data = json.loads(response.text)

        result = {}
        catalogs = []
        supplierCodes = []

        smile = data[0]['smiles']
        max = 0
        for item in data:
            item['catalog']['catalog_name'] = item['catalog']['short_name']

            if item['substance_purchasable'] > max:
                catalogs = [item['catalog']]
                supplierCodes = [item['supplier_code']]
                max = item['substance_purchasable']
        result['smiles'] = smile
        c = catalogs[0]

        result['supplier'] = [{
            'assigned': True,
            'cat_name': c['name'],
            'price': 240,
            'purchase': 1,
            'quantity': 10,
            'shipping': "6 weeks",
            'supplier_code': supplierCodes[0],
            'unit': "mg"
        }]
        result['catalogs'] = catalogs
        result['tranche'] = get_basic_tranche(smile)
        result['zinc20'] = True
        result['tranche_details'] = get_compound_details(smile)
        result['supplier_code'] = supplierCodes

        prices = [{
            'category_name': c['name'],
            'short_name': c['short_name'],
            'unit':'10mg',
            'price': '10.0',
            'shipping': '6 weeks',
            'supplier_code': supplierCodes[0]
        }]
        return result, result, smile, prices, []

    else:
        return None, None, None, None, []


def getZincData(identifier):
    task = send_task('app.data.tasks.search_zinc.getSubstanceList', [
                     [], [identifier]])
    res = task.get()

    if res:
        role = ''
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            role = 'ucsf'
        else:
            role = 'public'

        logs = res['zinc22']["logs"]

        if len(res['zinc22']["found"]) == 0:
            return None, None, None, None,  res['zinc22']["logs"]
        data = res['zinc22']["found"][0]

        prices = []
        if data.get('catalogs'):
            catalogs = data['catalogs']

            for i in range(len(catalogs)):
                c = catalogs[i]

                s = c['catalog_name'].lower()
                code = c['supplier_code']

                price = DefaultPrices.query.filter_by(
                    short_name=s, organization=role).first()

                if price:
                    newPrice = {
                        "category_name": price.category_name,
                        "supplier_code": code,
                        "quantity": price.quantity,
                        "unit": price.unit,
                        "shipping": price.shipping,
                        "price": price.price
                    }

                    prices.append(newPrice)

        # Some of the zinc22 mols are missing vendor data. In that case, use the Zinc20 results as backup.
        if(len(prices) >= 1):
            for price in prices:
                if 'ZINC' not in price['supplier_code']:
                    break
                else:
                    return getZinc20Data(code)

        smile = data['smiles'].encode('ascii')
        smile = smile.replace(b'\x01', b'\\1')
        smile = smile.decode()
        data['smiles'] = smile

        data['zinc20'] = False
        data['supplier'] = []

        return data, res, smile, prices, logs


@application.route('/sw')
def sw():
    try:
        config = requests.get(sw_server + '/search/config').json()
    except:
        return render_template('errors/500.html')
    try:
        maps = requests.get(sw_server + '/search/maps').json()
    except:
        return render_template('errors/500.html')
    smiles = request.args.get('smiles')
    print(smiles)
    return render_template('search/sw.html', config=json.dumps(config), maps=json.dumps(maps), sw_server=sw_server, withCredentials=False)


@application.route('/swp')
def swp():
    try:
        config = requests.get(swp_server + '/search/config',
                              auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/403.html')
    try:
        maps = requests.get(swp_server + '/search/maps',
                            auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/403.html')
    return render_template('search/sw.html', config=json.dumps(config), maps=json.dumps(maps), sw_server=swp_server, withCredentials=True)


@application.route('/swc')
def swc():
    try:
        config = requests.get(swc_server + '/search/config',
                              auth=('big', 'fat secret')).json()
    except:
        return render_template('errors/403.html')
    try:
        maps = requests.get(swc_server + '/search/maps',
                            auth=('big', 'fat secret')).json()
    except:
        return render_template('errors/403.html')
    return render_template('search/sw.html', config=json.dumps(config), maps=json.dumps(maps), sw_server=swc_server, withCredentials=True)


@application.route('/arthor')
def arthor():
    return render_template('search/arthor.html', arthor_url="https://arthor.docking.org")


@application.route('/arthorp')
def arthorp():
    return render_template('search/arthor.html', arthor_url="https://arthorp.docking.org")
