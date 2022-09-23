from unicodedata import category
from gevent import monkey
from celery.execute import send_task
from celery.result import AsyncResult
import socket
import grequests
from importlib import reload
reload(socket)
from app.data.models.vendors import Vendors
from sqlalchemy.sql.expression import true
from app.data.models.tin.catalog import CatalogModel
from flask import render_template, request, json, jsonify, flash, Markup
from app.main import application


import requests
from app.data.models.default_prices import DefaultPrices
from flask_login import current_user
import urllib.parse
import re

base_url = "https://cartblanche22.docking.org/"
swp_server = 'https://swp.docking.org'
swc_server = 'https://swc.docking.org'


# getting swp view, a section of a hit list, returning JSON for that range.
@application.route('/search/view')
def search_view():
    params = request.query_string.decode("utf-8")
    response = requests.get(swp_server + '/search/view', params=params, auth=('gpcr', 'xtal'))
    return response.json()


@application.route('/search/byzincid', methods=["GET", "POST"])
def search_byzincid():
    if request.method == "GET":
        text = Markup('Please contact jjiteam@googlegroups.com with molecules that won\'t look up. ' \
                      "For more information and updates, <a href=\"https://wiki.docking.org/index.php/Legacy_IDs_in_ZINC22\">check the docking wiki</a>.")
        
        flash(text)
        return render_template('search/search_byzincid.html')
    elif request.method == "POST":
        data = request.form['myTextarea']
        file = request.files['zincfile'].read().decode("utf-8")
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        fileDataList = file.split('\n')
        zinc22 = []
        zinc20 = []
        discarded = []
        zinc22_response, zinc20_response = None, None
        data22_json, data22 = None, None
        data20_json, data20 = None, None
        for identifier in textDataList + fileDataList:
            if '-' in identifier:
                def checkHasZinc(identifier):
                    if identifier[0:4].upper() != 'ZINC':
                        identifier_ = 'ZINC' + identifier
                        return identifier_.replace('-', (16 - len(identifier_) + 1) * '0')
                    return identifier.replace('-', (16 - len(identifier) + 1) * '0')
                new_identifier = checkHasZinc(identifier)
                print(new_identifier, identifier, len(new_identifier))
                zinc22.append(new_identifier)
                continue
            if identifier.isnumeric() or identifier[4:6] == '00':
                zinc20.append(identifier)
                continue
            elif identifier[0:4].upper() == 'ZINC':
                zinc22.append(identifier)
                continue
            else:
                discarded.append(identifier)
        if len(zinc22) > 0:
            files = {
                'zinc_id-in': ','.join(zinc22)
            }
            url = "https://cartblanche22.docking.org/sublist"
        
            print(zinc22)
            
            zinc22_response = requests.post(url, data=files)
        if len(zinc20) > 0:
            zinc20_files = {
                'zinc_id-in': zinc20,
                'output_fields': "zinc_id supplier_code smiles substance_purchasable"
            }
            zinc20_response = requests.post("https://zinc15.docking.org/catitems.txt", data=zinc20_files)
        if zinc22_response:
            zinc22_result = zinc22_response.json()
            if 'items' in zinc22_result:
                data22 = zinc22_result['items']
        if zinc20_response:
            zinc20_data = {}
            for line in zinc20_response.text.split('\n'):
                temp = line.split('\t')
                if len(temp) == 4:
                    identifier, supplier_code, smiles, purchasibility = temp[0], temp[1], temp[2], temp[3]
                    if identifier not in zinc20_data:
                        zinc20_data[identifier] = {
                            'identifier': identifier,
                            'zinc_id': identifier,
                            'smiles': smiles,
                            'catalogs_new': [{'supplier_code': supplier_code, 'purchasibility': purchasibility}],
                            'catalogs': supplier_code,
                            'supplier_code': supplier_code,
                            'db': 'zinc20'
                        }
                    else:
                        catalogs = zinc20_data[identifier]['catalogs_new']
                        cat_found = False
                        for c in catalogs:
                            if c['supplier_code'] == supplier_code:
                                cat_found = True
                        if not cat_found:
                            zinc20_data[identifier]['catalogs_new'].append({'supplier_code': supplier_code, 'purchasibility': purchasibility})
            data20 = list(zinc20_data.values())
        if data20 or data22:
            print(data20)
            return render_template('search/result_zincsearch.html', data22_json=json.dumps(data22), data22=data22,
                                   data20_json=json.dumps(data20), data20=data20)
        else:
            return render_template('errors/search404.html', lines=files, href='/search/search_byzincid',
                               header="We didn't find those molecules from Zinc22 database. Click here to return"), 404


@application.route('/search/bysmiles', methods=["GET", "POST"])
def search_bysmiles():
    if request.method == "GET":
        return render_template('search/search_bysmiles.html')
    elif request.method == "POST":
        data = request.form['smilesTextarea']
        file = request.files['smilesfile'].read().decode("utf-8")
        dist = request.form['dist']
        adist = request.form['adist']
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        fileDataList = file.split('\n')
        files = {
            'smiles-in': ','.join(textDataList + fileDataList),
            'dist': dist,
            'adist': adist,
        }
        # url = "https://cartblanche22.docking.org/smilelist"
        url = "http://localhost:5000/smilelist"
        response = requests.post(url, data=files)
        print(response)
        if response:
            print(response.json())
            smiles_result = response.json()
            return render_template('search/result_smiles.html', data_json=json.dumps(smiles_result), data=smiles_result)
        else:
            return render_template('errors/search404.html', lines=files, href='/search/search_bysmiles',
                               header="We didn't find those molecules from Zinc22 database. Click here to return"), 404


@application.route('/search/bysupplier', methods=["GET", "POST"])
def search_bysupplier():
    if request.method == "GET":
        text = Markup('Please contact jjiteam@googlegroups.com with molecules that won\'t look up. ' \
                      "For more information and updates, <a href=\"https://wiki.docking.org/index.php/Legacy_IDs_in_ZINC22\">check the docking wiki</a>.")
        
        flash(text)
        return render_template('search/search_bysupplier.html')
    elif request.method == "POST":
        data = request.form['supplierTextarea']
        file = request.files['supplierfile'].read().decode("utf-8")
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        # fileDataList = [x for x in re.split(' |, |,|\n,|\r, |\r\n', file) if x!='']
        fileDataList = file.split('\n')
        print('fileDataList', fileDataList)
        print('textDataList', textDataList)
        files = {
            'supplier_code-in': ','.join(textDataList + fileDataList),
        }
        url = "https://cartblanche22.docking.org/catlist"
        # url = 'https://{}/catlist'.format(request.host)
        response = requests.post(url, data=files)
        print(response)
        if response:
            print(response.json())
            supplier_result = response.json()
            found_molecules = []
            waited_servers =[]
            for s in supplier_result['items']:
                if 'error' not in s:
                    found_molecules.append(s)
                else:
                    temparr = s['elapsed_time'].split(' ')
                    time = float(temparr[-2])
                    if time >= 1:
                        waited_servers.append(s)
            return render_template('search/result_supplier.html', data_json=json.dumps(found_molecules),
                                   data=found_molecules, servers=waited_servers)
        else:
            return render_template('errors/search404.html', lines=files, href='/search/search_bysupplier',
                               header="We didn't find those molecules from Zinc22 database. Click here to return"), 404


@application.route('/search/zincid')
def search_zincid():
    return render_template('search/search_byzincid.html')


@application.route('/search/random')
def search_random():
    return render_template('search/search_random.html')


@application.route('/search/suppliercode')
def search_suppliercode():
    return render_template('search/search_suppliercode.html')


@application.route('/search/smiles')
def search_smiles():
    return render_template('search/search_smiles.html')


@application.route('/search/smiles/vendor')
def search_smiles_vendor():
    return render_template('search/search_smiles_vendor.html')

@application.route('/searchZinc20/<identifier>')
def searchZinc20(identifier):
    zinc20_files = {
            'zinc_id-in': [identifier],
            'output_fields': "zinc_id supplier_code smiles substance_purchasable catalog inchikey"
    }
    monkey.patch_socket()  
    response = requests.post("https://zinc20.docking.org/catitems/subsets/for-sale.json", data=zinc20_files)
    reload(socket)
    print(response)
    if response:
        role = ''
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            role = 'ucsf'
        else:
            role = 'public'
        data= json.loads(response.text)
        
        
        result = {}
        catalogs = []
        supplierCodes= []
        
        smile = data[0]['smiles']
        max = 0
        for item in data:
            item['catalog']['catalog_name'] = item['catalog']['short_name']
            cat = CatalogModel.query.filter_by(short_name = item['catalog']['short_name']).first()
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
        result['tranche'] = 'here'
        result['zinc20'] = true
        result['tranche_details'] = {}
        result['tranche_details']['inchi_key'] = data[0]['inchikey']
        result['supplier_code'] = supplierCodes
        
        
        prices = [{
                'category_name' : c['name'],
                'short_name': c['short_name'],
                'unit' :'10mg',
                'price': '10.0',
                'shipping': '6 weeks'
        }]
          
       
        return render_template('molecule/mol_index.html', data=result, prices=prices,
                               smile=urllib.parse.quote(smile), response=response, identifier=identifier, zinc20_stock='zinc20_stock')
    else:
        return render_template('errors/search404.html', lines=files, href='/search/zincid',
                               header="We didn't find this molecule from Zinc22 database. Click here to return"), 404

@application.route('/searchZinc/<identifier>')
def searchZinc(identifier):
    # files = {
    #     'zinc_id-in': [identifier]
    # }
   
    # using celery zincid search here
    data, res, smile, prices = getZincData(identifier)
    
    if data:
        return render_template('molecule/mol_index.html', data=data, prices=prices, 
                               smile=urllib.parse.quote(smile), response=res, identifier=identifier, zinc20_stock='zinc20_stock')
    else:
        return render_template('errors/search404.html', lines=files, href='/search/zincid',
                               header="We didn't find this molecule from Zinc22 database. Click here to return"), 404

def getZincData(identifier):
    task = send_task('app.data.tasks.search_zinc.getSubstanceList', [[], [identifier]]) 
    res = task.get()
    
    if res:
        role = ''
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            role = 'ucsf'
        else:
            role = 'public'
  
        data= res['zinc22']["found"][0]
        
        
        
        prices = []
        
        if data.get('catalogs'):
            catalogs = data['catalogs']
           
            for i in range(len(catalogs)):
                c = catalogs[i]
                
                s = c['catalog_name'].lower()
               
                price = DefaultPrices.query.filter_by(short_name=s, organization=role).first()
                print(price)
                if price:
                    prices.append(price)

                # if 'mcule' in s:
                #     prices.append(DefaultPrices.query.filter_by(category_name='mcule', organization=role).first())
                # elif 'wuxi' in s or 'w' in s:
                #     prices.append(DefaultPrices.query.filter_by(category_name='wuxi', organization=role).first())
                # elif 's' in s:
                #     prices.append(DefaultPrices.query.filter_by(category_name='Enamine_S', organization=role).first())
                # elif 'm' in s:
                #     prices.append(DefaultPrices.query.filter_by(category_name='Enamine_M', organization=role).first())
                # else:
                #     pass
                #     # prices.append(DefaultPrices.query.filter_by(category_name='mcule', organization=role).first())
        
        smile = data['smiles'].encode('ascii')
        smile = smile.replace(b'\x01', b'\\1')
        smile = smile.decode()
        data['smiles'] = smile
        
        data['zinc20']= False
        data['supplier']= []
        return data, res, smile, prices

@application.route('/sw')
def sw():
    return render_template('search/sw.html')


@application.route('/swp')
def swp():
    try:
        config = requests.get(swp_server + '/search/config', auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/500.html')
    try:
        maps = requests.get(swp_server + '/search/maps', auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/500.html')
    return render_template('search/swp.html', config=json.dumps(config), maps=json.dumps(maps))


@application.route('/swc')
def swc():
    try:
        config = requests.get(swc_server + '/search/config', auth=('big', 'fat secret')).json()
    except:
        return render_template('errors/403.html')
    try:
        maps = requests.get(swc_server + '/search/maps', auth=('big', 'fat secret')).json()
    except:
        return render_template('errors/403.html')
    return render_template('search/swc.html', config=json.dumps(config), maps=json.dumps(maps))


@application.route('/arthor')
def arthor():
    return render_template('search/arthor.html')
