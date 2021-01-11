from flask import render_template,  url_for, redirect, request
from app.main import application
from flask_login import current_user, login_required
from flask_user import roles_required
from app.data.forms.searchForms import SearchZincForm
import requests

base_url = "http://cartblanche22.docking.org/"

@application.route('/search/zincid')
def search_zincid():
    return render_template('search/search_zincid.html')


@application.route('/search/suppliercode')
def search_suppliercode():
    return render_template('search/search_suppliercode.html')


@application.route('/search/smiles')
def search_smiles():
    return render_template('search/search_smiles.html')

# @application.route('/search/', methods=["GET"])
# def search(var):
#     print(var)
#     if var == 'zinc':
#         form = searchZincForm()
#     elif var == 'file':
#         form = searchFileForm()
#     elif var == 'zinclist':
#         form = searchZincListForm()
#     return render_template('search/searchby.html', var=var, form=form)
#

@application.route('/searchZinc', methods=["POST"])
def searchZinc():
    formData = SearchZincForm(request.values)
    zinc_id = formData.zinc_id.data
    files = {
        'zinc_id': zinc_id
    }
    response = requests.get('http://{}/search.json'.format(request.host), params=files)
    # response = requests.get(base_url + 'search.json', params=files)
    if response:
        data = response.json()
        print(data)
        return render_template('search/search_result.html', data_=[data])
    else:
        return render_template('errors/404.html'), 404


@application.route('/searchZincList', methods=["POST"])
def searchZincList():
    zinc_ids = SearchZincForm(request.values).list_of_zinc_id.data
    uploaded_file = SearchZincForm(request.files).zinc_file.data
    if uploaded_file.filename == '':
        print('empty')
        files = {
            'zinc_id-in': zinc_ids
        }
    else:
        uploaded_file = uploaded_file.read().decode("latin-1")
        lines = uploaded_file.split('\n')
        files = {
            'zinc_id-in': ','.join(lines)
        }
    print(files)
    response = requests.post('http://{}/sublist'.format(request.host), params=files)
    # response = requests.post("http://cartblanche22.docking.org/sublist", params=files)
    print(response)
    if response:
        data = response.json()
        return render_template('search/search_result.html', data_=data['items'])
    else:
        return render_template('errors/404.html'), 404
    return render_template('search/search_zincid.html')


@application.route('/sw', methods=['GET', 'POST'])
def sw():
    # identifiers = []
    # for i in current_user.items_in_cart:
    #     identifiers.append(i.identifier)
    # return render_template('search/sw.html', items=identifiers)
    return render_template('search/sw.html')


@application.route('/swp', methods=['GET', 'POST'])
def swp():
    return render_template('search/swp.html')
    if current_user.has_roles('private'):
        # identifiers = []
        # for i in current_user.items_in_cart:
        #     identifiers.append(i.identifier)
        # return render_template('search/swp.html', items=identifiers)
        return render_template('search/swp.html')
    else:
        return redirect(url_for('main.sw'))


@application.route('/arthor', methods=['GET', 'POST'])
def arthor():
    # identifiers = []
    # for i in current_user.items_in_cart:
    #     identifiers.append(i.identifier)
    # return render_template('search/arthor.html', items=identifiers)
    return render_template('search/arthor.html')

