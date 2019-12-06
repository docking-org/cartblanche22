from flask import render_template,  url_for
from app.main import application
from flask_login import current_user, login_required
from flask_user import roles_required

@application.route('/sw', methods=['GET', 'POST'])
@login_required
def sw():
    identifiers = []
    for i in current_user.items_in_cart:
        identifiers.append(i.identifier)
    return render_template('sw.html', items=identifiers)

@application.route('/swp', methods=['GET', 'POST'])
@roles_required('admin')
def swp():
    identifiers = []
    for i in current_user.items_in_cart:
        identifiers.append(i.identifier)
    return render_template('swp.html', items=identifiers)


@application.route('/arthor', methods=['GET', 'POST'])
def arthor():
    identifiers = []
    for i in current_user.items_in_cart:
        identifiers.append(i.identifier)
    return render_template('arthor.html', items=identifiers)