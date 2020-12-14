from flask import render_template,  url_for, redirect, request
from app.main import application
from flask_login import current_user, login_required
from flask_user import roles_required
from app.data.forms.searchForms import searchZincForm, searchFileForm, searchZincListForm
import requests


@application.route('/search/<var>', methods=["GET"])
def search(var):
    print(var)
    if var == 'zinc':
        form = searchZincForm()
    elif var == 'file':
        form = searchFileForm()
    elif var == 'zinclist':
        form = searchZincListForm()
    return render_template('search/searchby.html', var=var, form=form)


@application.route('/searchZinc', methods=["POST"])
def searchZinc():
    print(request.form.getlist('id'))
    zinc_id = request.form.getlist('id')[0]
    files = {
        'zinc_id': zinc_id
    }
    response = requests.get('http://{}/search.json'.format(request.host), params=files)
    # response = requests.get('http://zinc22.docking.org/search.json', params=files)
    if response:
        data = response.json()
        print(data)
        return render_template('search/search_result.html', data_=[data])
    else:
        return render_template('errors/404.html'), 404


@application.route('/searchZincList', methods=["POST"])
def searchZincList():
    data_ = request.form.getlist('listData')[0].split('\r\n').strip()
    data = []
    for i in data_:
        if i != '':
            data.append(i)
    d = ','.join(data)
    print(d)
    files = {
        'zinc_id-in': d
    }
    response = requests.post('http://{}/sublist'.format(request.host), params=files)
    # response = requests.post('http://zinc22.docking.org/sublist', params=files)
    print(response)
    if response:
        data = response.json()
        print(data)
        return render_template('search/search_result.html', data_=data['items'])
    else:
        return render_template('errors/404.html'), 404
    return render_template('search/search_result.html')


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

