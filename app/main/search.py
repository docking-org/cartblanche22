from flask import render_template,  url_for, redirect
from app.main import application
from flask_login import current_user, login_required
from flask_user import roles_required

@application.route('/sw', methods=['GET', 'POST'])
@login_required
def sw():
    identifiers = []
    for i in current_user.items_in_cart:
        identifiers.append(i.identifier)
    return render_template('search/sw.html', items=identifiers)

@application.route('/swp', methods=['GET', 'POST'])
def swp():
    if current_user.has_roles('admin'):
        identifiers = []
        for i in current_user.items_in_cart:
            identifiers.append(i.identifier)
        return render_template('search/swp.html', items=identifiers)
    else:
        return redirect(url_for('main.sw'))


@application.route('/arthor', methods=['GET', 'POST'])
def arthor():
    identifiers = []
    for i in current_user.items_in_cart:
        identifiers.append(i.identifier)
    return render_template('search/arthor.html', items=identifiers)