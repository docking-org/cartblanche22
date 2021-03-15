from flask import render_template, request, json, redirect, url_for, session, Response
from app.main import application
from app.data.forms.searchForms import SearchZincForm, SearchSmilesForm, SearchSupplierForm, SearchRandom
import requests
import re
from app.data.models.default_prices import DefaultPrices
from flask_login import current_user

base_url = "http://cartblanche22.docking.org/"
swp_server = 'http://swp.docking.org'
sw_server = 'http://swp.docking.org'


@application.route('/search/example')
def search_example():
    return render_template('search/search_result_example.html')


@application.route('/search/mol/example')
def search_mol_example():
    return render_template('molecule/mol_example.html')


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
            'count': amount
        }
        try:
            response = requests.post('http://cartblanche22.docking.org/substance/random.txt', params=files, timeout=15)
            print(response)
            print(response.data)
            # data = response.json()
            # print(data)
            data = ''
            download_filename = 'random.txt'
            response = Response(json.dumps(data), mimetype='text/plain')
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
            return response
        except requests.exceptions.Timeout as e:
            print(e)
            return render_template('errors/404.html', desc='Random search is not working due to server overload', lines='random not working'), 404


@application.route('/search/suppliercode')
def search_suppliercode():
    return render_template('search/search_suppliercode.html')


@application.route('/search/smiles')
def search_smiles():
    return render_template('search/search_smiles.html')


@application.route('/searchZinc', methods=["POST", "GET"])
def searchZinc():
    if request.method == "POST":
        print('searchZinc')
        formData = SearchZincForm(request.values)
        zinc_id = formData.zinc_id.data
        zinc_id = zinc_id.replace(" ", "")
    else:
        zinc_id = request.values.get('zinc_id')
    files = {
            'zinc_id': zinc_id
    }
    response = requests.get(base_url + 'search.json', params=files)
    if response:
        prices = None
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            prices = DefaultPrices.query.filter_by(organization='ucsf')
        else:
            prices = DefaultPrices.query.filter_by(organization='public')
        data = response.json()
        print(data)
        return render_template('molecule/mol_index.html', data=data['items'][0], prices=prices)
    else:
        return render_template('errors/search404.html', lines=files), 404


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
    return render_template('search/swp.html')
    try:
        config = requests.get('https://swp.docking.org/search/config', auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/500.html')
    try:
        maps = requests.get('https://swp.docking.org/search/maps', auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/500.html')
    return render_template('search/swp.html', config=json.dumps(config), maps=json.dumps(maps))


@application.route('/arthor', methods=['GET', 'POST'])
def arthor():
    return render_template('search/arthor.html')
