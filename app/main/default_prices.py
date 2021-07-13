from flask import redirect, jsonify, request, url_for, session, render_template
from app.main import application
from app.data.models.default_prices import DefaultPrices
from flask_login import current_user


@application.route("/getDefaultPrices", methods=['GET'])
def getDefaultPrices():
    role = ''
    if current_user.is_authenticated and current_user.has_roles('ucsf'):
        role = 'ucsf'
    else:
        role = 'public'
    prices = DefaultPrices.query.filter_by(organization=role).all()
    return jsonify(prices)
