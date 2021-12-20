from flask import abort, jsonify, render_template
from flask_login import current_user, login_required
from app.main import application
from app import db
from app.data.models.carts import Carts
import requests
import urllib.parse

@application.route('/importData', methods=["GET"])
@login_required
def importData():
     return render_template('cart/import.html')


@application.route('/importIdentifier/<identifier>', methods=['POST'])
def importIdentifier(identifier):

    print(identifier)
    try:
        identifier, img, db = validator(identifier)
    except TypeError as err:
        return jsonify('fail')
    activeCart = Carts.query.get(current_user.activeCart)
    item_id = activeCart.addToCart(current_user, identifier, img, db)
    if item_id == False:
        return jsonify('exists') 
    return jsonify(item_id)


def validator(identifier):
    print('validating ', identifier)
    identifier = identifier.lower()
    if 'c' in identifier or 'identifier' in identifier or identifier.isnumeric():
        response = requests.get('https://zinc15.docking.org/substances/'+identifier+'.txt')
        if response:
            identifier, smile = response.text.split()[0], response.text.split()[1]
            db = 'ZINC-All-19Q4-1.4B.anon'
            img = 'https://sw.docking.org/depict/svg?w=50&h=30&smi={}%20{}8&qry=&cols=&cmap=&bgcolor=clear&hgstyle=outerglow'.\
                format(urllib.parse.quote(smile),identifier)
            return identifier, img, db
    else:
        response = requests.get('http://prices.docking.org/api/_search_btz', params={'molecule_id': identifier})
        molecule = response.json()
        if response and molecule['db_name']:
            identifier = molecule['mol_id']
            smile = molecule['smiles']
            db = molecule['db_name']
            img = 'https://sw.docking.org/depict/svg?w=50&h=30&smi={}%20{}8&qry=&cols=&cmap=&bgcolor=clear&hgstyle=outerglow'.\
                format(urllib.parse.quote(smile),identifier)
            return identifier, img, db
    return False
