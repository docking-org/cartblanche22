from flask import render_template, request, json, redirect, url_for, session, Response, jsonify
from app.main import application
from app.data.forms.searchForms import SearchZincForm, SearchSmilesForm, SearchSupplierForm, SearchRandom
import requests
import re
from app.data.models.default_prices import DefaultPrices
from flask_login import current_user
import urllib.parse

base_url = "https://cartblanche22.docking.org/"
swp_server = 'https://swp.docking.org'
sw_server = 'https://swp.docking.org'

@application.route('/search/api')
def search_api():
    data = [
        {"catalogs":[{"catalog_name":"m","short_name":"m"}],
         "smiles":"C=C(C)CN(C)[C@H](C)CNC(=O)c1nc(C)n2ccccc12",
         "supplier_code":["m_275030__14114248__14126248__12659170"],
         "tranche":{"h_num":"H22","logp":"s","mwt":"m","p_num":"P220"},
         "zinc_id":"ZINCms000002NiP3"
         },
        {"catalogs": [{"catalog_name": "m", "short_name": "m"}],
         "smiles": "C=C(C)CN(C)[C@H](C)CNC(=O)c1nc(C)n2ccccc12",
         "supplier_code": ["m_275030__14114248__14126248__12659170"],
         "tranche": {"h_num": "H22", "logp": "s", "mwt": "m", "p_num": "P220"},
         "zinc_id": "ZINCms000002NiP4"
         },
        {"catalogs": [{"catalog_name": "m", "short_name": "m"}],
         "smiles": "C=C(C)CN(C)[C@H](C)CNC(=O)c1nc(C)n2ccccc12",
         "supplier_code": ["m_275030__14114248__14126248__12659170"],
         "tranche": {"h_num": "H22", "logp": "s", "mwt": "m", "p_num": "P220"},
         "zinc_id": "ZINCms000002NiP5"
         },
        {"catalogs": [{"catalog_name": "m", "short_name": "m"}],
         "smiles": "C=C(C)CN(C)[C@H](C)CNC(=O)c1nc(C)n2ccccc12",
         "supplier_code": ["m_275030__14114248__14126248__12659170"],
         "tranche": {"h_num": "H22", "logp": "s", "mwt": "m", "p_num": "P220"},
         "zinc_id": "ZINCms000002NiP6"
         },
        {"catalogs": [{"catalog_name": "m", "short_name": "m"}],
         "smiles": "C=C(C)CN(C)[C@H](C)CNC(=O)c1nc(C)n2ccccc12",
         "supplier_code": ["m_275030__14114248__14126248__12659170"],
         "tranche": {"h_num": "H22", "logp": "s", "mwt": "m", "p_num": "P220"},
         "zinc_id": "ZINCms000002NiP7"
         },
        {"catalogs": [{"catalog_name": "m", "short_name": "m"}],
         "smiles": "C=C(C)CN(C)[C@H](C)CNC(=O)c1nc(C)n2ccccc12",
         "supplier_code": ["m_275030__14114248__14126248__12659170"],
         "tranche": {"h_num": "H22", "logp": "s", "mwt": "m", "p_num": "P220"},
         "zinc_id": "ZINCms000002NiP8"
         },
    ]
    return jsonify({'items': data})


@application.route('/search/view')
def search_view():
    params = request.query_string.decode("utf-8")
    response = requests.get(swp_server + '/search/view', params=params, auth=('gpcr', 'xtal'))
    return response.json()


@application.route('/search/zincid')
def search_zincid():
    return render_template('search/search_zincid.html')


@application.route('/search/random', methods=["POST", "GET"])
def search_random():
    if request.method == 'GET':
        return render_template('search/search_random.html')
    elif request.method == 'POST':
        amount = SearchRandom(request.values).amount.data
        print(amount)
        files = {
            'count': 10
        }
        try:
            response = requests.post('https://cartblanche22.docking.org/substance/random.json', params=files)
            print('worked')
            print(response)
            # print(response.data)
            data = response.json()
            # print(data)
            download_filename = 'random.txt'
            response = Response(json.dumps(data), mimetype='text/plain')
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
            return response
        except:
            return render_template('errors/404.html', desc='Random search is not working.', lines='random not working'), 404


@application.route('/search/suppliercode')
def search_suppliercode():
    return render_template('search/search_suppliercode.html')


@application.route('/search/smiles')
def search_smiles():
    return render_template('search/search_smiles.html')\


@application.route('/search/smiles/vendor')
def search_smiles_vendor():
    return render_template('search/search_smiles_vendor.html')


@application.route('/searchZinc/<identifier>', methods=["GET"])
def searchZinc(identifier):
    # zinc_id = request.values.get('zinc_id')
    print(identifier)
    files = {
            'zinc_id': identifier
    }
    response = requests.get(base_url + 'search.json', params=files)
    if response:
        prices = None
        role = ''
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            role = 'ucsf'
        else:
            role = 'public'
        data = response.json()
        supplier_codes = data['items'][0]['supplier_code']
        print(data)
        print(supplier_codes)
        prices = []
        for s in supplier_codes:
            if 'mcule' in s.lower():
                prices.append(DefaultPrices.query.filter_by(category_name='mcule', organization=role).first())
            elif 'w' in s.lower():
                prices.append(DefaultPrices.query.filter_by(category_name='wuxi', organization=role).first())
            elif 's' in s.lower():
                prices.append(DefaultPrices.query.filter_by(category_name='Enamine_S', organization=role).first())
            elif 'm' in s.lower():
                prices.append(DefaultPrices.query.filter_by(category_name='Enamine_M', organization=role).first())
        smile = data['items'][0]['smiles']
        return render_template('molecule/mol_index.html', data=data['items'][0], prices=prices, smile=urllib.parse.quote(smile))
    else:
        return render_template('errors/search404.html', lines=files, href='/search/zincid', header="We didn't find this molecule from Zinc22 database. Click here to return"), 404


@application.route('/searchSmilesList', methods=["POST"])
def searchSmilesList():
    smiles = SearchSmilesForm(request.values).list_of_smiles.data
    dist = SearchSmilesForm(request.values).dist.data
    adist = SearchSmilesForm(request.values).adist.data
    uploaded_file = SearchSmilesForm(request.files).smiles_file.data
    print(dist, adist, smiles)
    if uploaded_file.filename == '':
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', smiles)
    else:
        uploaded_file = uploaded_file.read().decode("latin-1")
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', uploaded_file)
    value = ','.join(lines)
    return redirect(url_for('main.showSmilesResult', value=value, dist=dist, adist=adist))


@application.route('/searchSupplierList', methods=["POST"])
def searchSupplierList():
    print('searchSupplierList')
    supplier_codes = SearchSupplierForm(request.values).list_of_suppliercode.data
    uploaded_file = SearchSupplierForm(request.files).supplier_file.data
    if uploaded_file.filename == '':
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', supplier_codes)
    else:
        uploaded_file = uploaded_file.read().decode("latin-1")
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', uploaded_file)
    value = ','.join(lines)
    return redirect(url_for('main.showSupplierResult', value=value))


@application.route('/searchZincList', methods=["POST", "GET"])
def searchZincList():
    print('searchZincList')
    zinc_ids = SearchZincForm(request.values).list_of_zinc_id.data
    uploaded_file = SearchZincForm(request.files).zinc_file.data
    if uploaded_file.filename == '':
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', zinc_ids)
    else:
        uploaded_file = uploaded_file.read().decode("latin-1")
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', uploaded_file)
    value = ','.join(lines)
    return redirect(url_for('main.showZincListResult', value=value))


@application.route('/sw', methods=['GET', 'POST'])
def sw():
    return render_template('search/sw.html')
    print('sw')
    config = requests.get('https://sw.docking.org/search/config').json()
    maps = requests.get('https://sw.docking.org/search/maps').json()
    print(config)
    print(maps)
    try:
        config = requests.get('https://sw.docking.org/search/config').json()
    except:
        return render_template('errors/500.html')
    try:
        maps = requests.get('https://sw.docking.org/search/maps').json()
    except:
        return render_template('errors/500.html')
    print(json.dumps(config))
    print(json.dumps(maps))
    return render_template('search/sw.html', config=json.dumps(config), maps=json.dumps(maps)), 200



@application.route('/swp', methods=[    'GET', 'POST'])
def swp():
    # return render_template('search/swp.html')
    try:
        config = requests.get('https://swp.docking.org/search/config', auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/500.html')
    try:
        maps = requests.get('https://swp.docking.org/search/maps', auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/500.html')
    print(config)
    print(maps)
    return render_template('search/swp.html', config=json.dumps(config), maps=json.dumps(maps))


@application.route('/arthor', methods=['GET', 'POST'])
def arthor():
    return render_template('search/arthor.html')
