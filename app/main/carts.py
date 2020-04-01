from flask import render_template, flash, redirect, url_for, jsonify, request, send_file
from app.main import application
from flask_login import current_user
from app.data.models.carts import Carts
from app.data.models.items import Items
from app.main.punchout import punchoutOrder
import csv, os
import re, requests
import urllib.parse


@application.route('/cart', methods= ['GET',  'POST'])
def cart():
    items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
    totalPrices=[]
    totalQuantities=[]
    punchoutOrderMessage, url = punchoutOrder()
    return render_template('cart/cart.html', data=items, prices=totalPrices, quantities=totalQuantities, punchoutOrderMessage=punchoutOrderMessage, url=url)

@application.route('/carts', methods= ['GET',  'POST'])
def carts():
    carts = Carts.query.filter_by(user_fk=current_user.id).all()
    for i in range(len(carts)):
        if carts[i].cart_id == current_user.activeCart:
            carts[i], carts[0] = carts[0], carts[i]
            break
    return render_template('cart/carts.html', carts=carts)

@application.route('/createCart', methods= ['GET'])
def createCart():
    Carts.createCart(current_user)
    return redirect(url_for('main.carts'))

@application.route('/renameCart', methods= ['POST'])
def renameCart():
    data = request.get_json()
    Carts.query.get(data['cart_id']).setName(data['name'])
    return jsonify('Cart name successfully updated')

@application.route('/deleteCart/<cart_id>', methods= ['DELETE'])
def deleteCart(cart_id):
    Carts.query.get(cart_id).deleteCart()
    print('cart deleted')
    return jsonify('success')

@application.route('/activateCart/<cart_id>', methods= ['GET'])
def activateCart(cart_id):
    current_user.setCart(cart_id)
    return redirect(url_for('main.carts'))

# @application.route('/importData', methods=['GET', 'POST'])
# def importData():
#     if request.method=="POST":
#         data = request.form['dataInput']
#         file = request.files['myfile'].read().decode("utf-8")
#         textDataList = [x for x in re.split(' |, |,|\n', data) if x!='']
#         fileDataList = [x for x in re.split(' |, |,|\n', file) if x!='']
#         wholeData = textDataList + fileDataList
#         # print(wholeData)
#         oldCart = current_user.activeCart
#         newCart = Carts.createCart(current_user)
#         molecules = []
#         validDataList = []
#         invalidDataList =[]
#         for data in wholeData:
#             isDataValid = False
#             lower = data.lower().strip()
#             if 'c' in lower or 'zinc' in lower or lower.isnumeric():
#                 response = requests.get('http://zinc15.docking.org/substances/'+data+'.txt')
#                 if response and response.text.split()[0] not in molecules:
#                     identifier, smile = response.text.split()[0], response.text.split()[1]
#                     molecules.append(identifier)
#                     db = 'ZINC-All-19Q4-1.4B.anon'
#                     img = 'http://sw.docking.org/depict/svg?w=50&h=30&smi={}%20{}8&qry=&cols=&cmap=&bgcolor=clear&hgstyle=outerglow'.format(urllib.parse.quote(smile),identifier)
#                     item_id = newCart.addToCart(current_user, identifier ,img, db)
#                     # requests.post(url = 'http://0.0.0.0:5067/autoChooseVendor/'+str(item_id))
#                     isDataValid = True
#                 # if response and response.text.split()[0] not in zincDB.keys():
#                 #     zincDB[response.text.split()[0]] = response.text.split()[1]
#             # else:
#             #     response = requests.get('http://gimel.compbio.ucsf.edu:5022/api/_search_btz', params={'molecule_id':lower})
#             #     molecule = response.json()
#             #     if response and molecule['db_name']:
#             #         identifier = molecule['mol_id']
#             #         molecules.append(identifier)
#             #         smile = molecule['smiles']
#             #         db = molecule['db_name']
#             #         img = 'http://sw.docking.org/depict/svg?w=50&h=30&smi={}%20{}8&qry=&cols=&cmap=&bgcolor=clear&hgstyle=outerglow'.format(urllib.parse.quote(smile),identifier)
#             #         item_id = newCart.addToCart(current_user, identifier ,img, db)
#             #         requests.post(url = 'http://0.0.0.0:5067/autoChooseVendor/'+str(item_id))
#                         # isDataValid = True
#             if isDataValid:
#                 validDataList.append(data)
#             else:
#                 invalidDataList.append(data)
#         if len(molecules) == 0:
#             current_user.activeCart = oldCart
#             newCart.deleteCart()
#         # if zincDB:
#         #     activeCart = Carts.createCart(current_user)
#         #     db = 'ZINC-All-19Q4-1.4B.anon'
#         #     for identifier, smile in zincDB.items():
#         #         img = 'http://sw.docking.org/depict/svg?w=50&h=30&smi={}%20{}8&qry=&cols=&cmap=&bgcolor=clear&hgstyle=outerglow'.format(urllib.parse.quote(smile),identifier)
#         #         item_id = activeCart.addToCart(current_user, identifier ,img, db)
#         #         requests.post(url = 'http://0.0.0.0:5067/autoChooseVendor/'+str(item_id))
#                 # identifier = response.text.split()[0]
#         # return redirect(url_for('main.cart'))       
#         return render_template('cart/importResult.html', textDataList = textDataList, fileDataList= fileDataList)
#     else:
#         return render_template('cart/import.html')