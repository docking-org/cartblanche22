from flask import render_template, request, json, jsonify
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

@application.route('/search/search_byzincid', methods=["GET", "POST"])
def search_byzincid():
    if request.method == "GET":
        return render_template('search/search_byzincid.html')
    elif request.method == "POST":
        data = request.form['myTextarea']
        file = request.files['zincfile'].read().decode("utf-8")
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        # fileDataList = [x for x in re.split(' |, |,|\n,|\r, |\r\n', file) if x!='']
        fileDataList = file.split('\n')
        print(fileDataList)
        print(len(fileDataList))
        zinc22 = []
        zinc20 = []
        discarded = []
        for identifier in textDataList + fileDataList:
            if identifier.isnumeric() or identifier[4:6] == '00':
                zinc20.append(identifier)
                continue
            elif identifier[0:4].upper() == 'ZINC':
                zinc22.append(identifier)
                continue
            else:
                discarded.append(identifier)
        files = {
            'zinc_id-in': ','.join(zinc22)
        }
        # url = 'https://{}/sublist'.format(request.host)
        url = "https://cartblanche22.docking.org/sublist"
        response = requests.post(url, data=files)
        print(response)
        if response:
            print(response.json())
            zinc22_result = response.json()
            if 'items' in zinc22_result:
                return render_template('search/result_zincsearch.html', data_json=json.dumps(zinc22_result['items']), data=zinc22_result['items'] )
        else:
            return render_template('errors/search404.html', lines=files, href='/search/search_byzincid',
                               header="We didn't find those molecules from Zinc22 database. Click here to return"), 404


@application.route('/search/search_bysmiles', methods=["GET", "POST"])
def search_bysmiles():
    if request.method == "GET":
        return render_template('search/search_bysmiles.html')
    elif request.method == "POST":
        data = request.form['smilesTextarea']
        file = request.files['smilesfile'].read().decode("utf-8")
        dist = request.form['dist']
        adist = request.form['adist']
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        # fileDataList = [x for x in re.split(' |, |,|\n,|\r, |\r\n', file) if x!='']
        fileDataList = file.split('\n')
        print('fileDataList', fileDataList)
        print('textDataList', textDataList)
        print('dist', dist)
        print('adist', adist)
        files = {
            'smiles-in': ','.join(textDataList + fileDataList),
            'dist': dist,
            'adist': adist,

        }
        url = "https://cartblanche22.docking.org/smilelist"
        response = requests.post(url, data=files)
        print(response)
        if response:
            print(response.json())
            smiles_result = response.json()
            return render_template('search/result_smiles.html', data_json=json.dumps(smiles_result), data=smiles_result)
        else:
            return render_template('errors/search404.html', lines=files, href='/search/search_bysmiles',
                               header="We didn't find those molecules from Zinc22 database. Click here to return"), 404


@application.route('/search/search_bysupplier', methods=["GET", "POST"])
def search_bysupplier():
    if request.method == "GET":
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


@application.route('/searchZinc/<identifier>')
def searchZinc(identifier):
    files = {
        'zinc_id': identifier
    }
    # url = 'http://{}/search.json'.format(request.host)
    url = base_url + 'search.json'
    print(url)
    print(identifier)
    response = requests.get(url, params=files)
    if response:
        role = ''
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            role = 'ucsf'
        else:
            role = 'public'
        print(response)
        data = response.json()
        print(data)
        catalogs = data['items'][0]['catalogs']
        prices = []
        zinc20_stock = None
        for i in range(len(catalogs)):
            c = catalogs[i]
            s = c['catalog_name'].lower()
            prices.append(DefaultPrices.query.filter_by(short_name=s, organization=role).first())
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
        print(zinc20_stock)
        smile = data['items'][0]['smiles']
        print('data', data['items'][0])
        print('prices', prices)
        print('response', response)
        print('identifer', identifier)
        return render_template('molecule/mol_index.html', data=data['items'][0], prices=prices,
                               smile=urllib.parse.quote(smile), response=response, identifier=identifier, zinc20_stock='zinc20_stock')
    else:
        return render_template('errors/search404.html', lines=files, href='/search/zincid',
                               header="We didn't find this molecule from Zinc22 database. Click here to return"), 404


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
