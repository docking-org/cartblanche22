from flask import render_template, request, json
from app.main import application
import requests
from app.data.models.default_prices import DefaultPrices
from flask_login import current_user
import urllib.parse

base_url = "https://cartblanche22.docking.org/"
swp_server = 'https://swp.docking.org'


# getting swp view, a section of a hit list, returning JSON for that range.
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


@application.route('/search/smiles/vendor')
def search_smiles_vendor():
    return render_template('search/search_smiles_vendor.html')


@application.route('/searchZinc/<identifier>')
def searchZinc(identifier):
    files = {
        'zinc_id': identifier
    }
    response = requests.get(base_url + 'search.json', params=files)
    if response:
        role = ''
        if current_user.is_authenticated and current_user.has_roles('ucsf'):
            role = 'ucsf'
        else:
            role = 'public'
        data = response.json()
        supplier_codes = data['items'][0]['supplier_code']
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
        return render_template('molecule/mol_index.html', data=data['items'][0], prices=prices,
                               smile=urllib.parse.quote(smile))
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


@application.route('/arthor')
def arthor():
    return render_template('search/arthor.html')
