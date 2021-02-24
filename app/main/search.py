from flask import render_template, request, json
from app.main import application
from app.data.forms.searchForms import SearchZincForm, SearchSmilesForm, SearchSupplierForm
import requests
import re

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


@application.route('/search/random')
def search_random():
    return render_template('search/search_random.html')


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
        data = response.json()
        print(data)
        return render_template('molecule/mol_index.html', data=data[0])
    else:
        return render_template('errors/search404.html', lines=files), 404


@application.route('/searchSmilesList', methods=["POST"])
def searchSmilesList():
    print('searchSmilesList')
    smiles = SearchSmilesForm(request.values).list_of_smiles.data
    uploaded_file = SearchSmilesForm(request.files).smiles_file.data
    if uploaded_file.filename == '':
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', smiles)
        files = {
            'smiles-in': ','.join(lines),
            'dist': '0'
        }
        print(lines)
    else:
        uploaded_file = uploaded_file.read().decode("latin-1")
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', uploaded_file)
        files = {
            'smiles-in': ','.join(lines),
            'dist': '0'
        }
    response = requests.post(base_url + "smilelist", params=files)
    if response:
        data = response.json()
        print(data)
        return render_template('search/search_result_smile.html', data_=data)
    else:
        print(response)
        return render_template('errors/search404.html', lines=lines), 404
    return render_template('search/search_smiles.html')


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
    files = {
        'supplier_code-in': ','.join(lines),
    }
    response = requests.post(base_url + 'smilelist', params=files)
    if response:
        data = response.json()
        print(data)
        return render_template('search/search_result.html', data_=data['items'])
    else:
        print(response)
        return render_template('errors/search404.html', lines=lines), 404
    return render_template('search/search_suppliercode.html')


@application.route('/searchZincList', methods=["POST"])
def searchZincList():
    print('searchZincList')
    zinc_ids = SearchZincForm(request.values).list_of_zinc_id.data
    uploaded_file = SearchZincForm(request.files).zinc_file.data
    if uploaded_file.filename == '':
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', zinc_ids)
    else:
        uploaded_file = uploaded_file.read().decode("latin-1")
        lines = re.split('; |, |\*|\n|\r|,| |\t|\.', uploaded_file)
    files = {
        'zinc_id-in': ','.join(lines)
    }
    response = requests.post(base_url + "sublist", params=files)
    if response:
        data = response.json()
        print(data)
        return render_template('search/search_result.html', data_=data['items'])
    else:
        print(response)
        return render_template('errors/search404.html', lines=lines), 404
    return render_template('search/search_zincid.html')


@application.route('/sw', methods=['GET', 'POST'])
def sw():
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
