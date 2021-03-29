from flask import render_template,  url_for, redirect
from app.main import application
from flask_login import current_user, login_required
from flask_user import roles_required


@application.route('/search/zincid')
def search_zincid():
    return render_template('search/search_zincid.html')


@application.route('/search/suppliercode')
def search_suppliercode():
    return render_template('search/search_suppliercode.html')


@application.route('/search/smiles')
def search_smiles():
    return render_template('search/search_smiles.html')

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
