from flask import render_template, url_for, jsonify, request
from app.main import application
from flask_login import current_user
from app.data.models.carts import Carts
from app.data.models.items import Items
from app.data.models.vendors import Vendors
from app.main.punchout import punchoutOrder
from app.main.items import addToCartWithVendor
from app import db


@application.route('/addItem', methods=['POST'])
def addItem():
    item = request.get_json()['data']
    print('adding item:  ', item)
    new_item = Items(cart_fk=current_user.activeCart, identifier=item['identifier'], compound_img=item['smile'],
                     database=item['db'])
    db.session.add(new_item)
    db.session.commit()
    for s in item['supplier']:
        vendor = Vendors(item_fk=new_item.item_id, cat_name=s['cat_name'],
                         purchase_quantity=s['quantity'],
                         supplier_code=s['supplier_code'], price=float(s['price']),
                         pack_quantity=float(s['quantity']), unit=s['unit'], shipping_str=s['shipping'])
        db.session.add(vendor)
        db.session.commit()
        print('add vendor for new item')
    return jsonify('successfully added item to cart db')


@application.route('/addVendorTest', methods=['POST'])
def addVendorTest():
    if current_user.is_authenticated:
        data = request.get_json()['data']
        identifier = data['identifier']
        sup = data['sup']
        item = Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first()
        vendor = Vendors(item_fk=item.item_id, cat_name=sup['cat_name'],
                         purchase_quantity=sup['purchase'],
                         supplier_code=sup['supplier_code'], price=float(sup['price']),
                         pack_quantity=float(sup['quantity']), unit=sup['unit'], shipping_str=sup['shipping'])
        db.session.add(vendor)
        db.session.commit()
        print('adding vendor:  ', vendor)
        return jsonify('successfully added vendor to db')
    return jsonify("user not logged in")


@application.route('/deleteItemTest', methods=['DELETE'])
def deleteItemTest():
    if current_user.is_authenticated:
        data = request.get_json()['data']
        identifier = data['identifier']
        Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first().deleteItem()
        return jsonify('successfully deleted an item from db')
    return jsonify("user not logged in")


@application.route('/deleteVendorTest', methods=['POST'])
def deleteVendorTest():
    if current_user.is_authenticated:
        data = request.get_json()['data']
        item = Items.query.filter_by(identifier=data['identifier'], cart_fk=current_user.activeCart).first()
        vendors = Vendors.query.filter_by(item_fk=item.item_id).all()
        if len(vendors) <= 1:
            item.deleteItem()
        else:
            vendor = Vendors.query.filter_by(item_fk=item.item_id, cat_name=data['cat_name'],
                                             supplier_code=data['supplier_code'], price=float(data['price']),
                                             pack_quantity=float(data['quantity']), unit=data['unit']).first()
            vendor.deleteVendor()
        return jsonify('successfully deleted vendor from db')
    return jsonify("user not logged in")


@application.route('/updateVendorTest', methods=['POST'])
def updateVendorTest():
    if current_user.is_authenticated:
        data = request.get_json()['data']
        identifier = data['identifier']
        item = Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first()
        print(data)
        vendor = Vendors.query.filter_by(item_fk=item.item_id, cat_name=data['cat_name'],
                                         supplier_code=data['supplier_code'], price=float(data['price']),
                                         pack_quantity=float(data['quantity']), unit=data['unit']).first()
        vendor.updatePurchaseQuantity(data['purchase'])
    return jsonify('successfully updated vendor purchase to db')


@application.route('/saveCartToDbTest', methods=['POST'])
def saveCartToDbTest():
    print('saveCartToDB')
    data = request.get_json()['totalCart']
    print(data)
    for d in data:
        item = Items.query.filter_by(identifier=d['identifier'], cart_fk=current_user.activeCart).first()
        if item:
            suppliers = d['supplier']
            if len(suppliers) > 0:
                for s in suppliers:
                    vendor = Vendors.query.filter_by(cat_name=s['cat_name'], supplier_code=s['supplier_code'],price=s[
                            'price'], pack_quantity=s['quantity'], unit=s['unit'], shipping_str=s[
                            'shipping']).first()
                    if vendor:
                        vendor.updatePurchaseQuantity(max(s['purchase'], vendor.purchase_quantity))
                    else:
                        vendor = Vendors(item_fk=item.item_id, cat_name=s['cat_name'],
                                         purchase_quantity=s['purchase'],
                                         supplier_code=s['supplier_code'], price=float(s['price']),
                                         pack_quantity=float(s['quantity']), unit=s['unit'], shipping_str=s['shipping'])
                        db.session.add(vendor)
                        db.session.commit()
                        print('added vendor in found item')
        else:
            new_item = Items(cart_fk=current_user.activeCart, identifier=d['identifier'], compound_img=d['smile'],
                             database=d['db'])
            db.session.add(new_item)
            db.session.commit()
            print('add item: ', d['identifier'])
            print('new_item: ',new_item)
            suppliers = d['supplier']
            for s in suppliers:
                vendor = Vendors(item_fk=new_item.item_id, cat_name=s['cat_name'],
                                 purchase_quantity=s['purchase'],
                                 supplier_code=s['supplier_code'], price=float(s['price']),
                                 pack_quantity=float(s['quantity']), unit=s['unit'], shipping_str=s['shipping'])
                db.session.add(vendor)
                db.session.commit()
                print('add vendor for new item')
    response = populateCart()
    return jsonify(response)


@application.route('/cart', methods=['GET',  'POST'])
def cart():
    return render_template('cart/shoppingcart.html')

# @application.route('/cart', methods= ['GET',  'POST'])
# def cart():
#     items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
#     totalPrices=[]
#     totalQuantities=[]
#     punchoutOrderMessage, url = punchoutOrder()
#     return render_template('cart/cart.html', data=items, prices=totalPrices, quantities=totalQuantities, punchoutOrderMessage=punchoutOrderMessage, url=url)

@application.route('/carts', methods= ['GET',  'POST'])
def carts():
    carts = Carts.query.filter_by(user_fk=current_user.id).all()
    print(carts)
    result = []
    for c in carts:
        print(c.name)
        cart = {
            'name' : c.name,
            'qty' : c.count,
            'total' : c.totalPrice,
            'status' : c.status,
            'DT_RowId' : c.cart_id
        }
        if c.cart_id == current_user.activeCart:
            cart['active'] = True
            result.insert(0, cart)
        else:
            cart['active'] = False
            result.append(cart)
    return render_template('cart/carts.html', carts=carts, result = result)

@application.route('/createCart', methods= ['GET'])
def createCart():
    Carts.createCart(current_user)
    return jsonify(url_for('main.carts'))

@application.route('/renameCart', methods= ['POST'])
def renameCart():
    data = request.get_json()
    print(data['name'])
    Carts.query.get(data['cart_id']).setName(data['name'])
    return jsonify('Cart name successfully updated')

@application.route('/deleteCart/<cart_id>', methods= ['DELETE'])
def deleteCart(cart_id):
    Carts.query.get(cart_id).deleteCart()
    print('cart deleted')
    return jsonify('success')

@application.route('/activateCart/<cart_id>', methods= ['GET'])
def activateCart(cart_id):
    print(cart_id)
    current_user.setCart(cart_id)
    response = populateCart()
    return jsonify({'data':response})

def populateCart():
    response = []
    if current_user.is_authenticated:
        cart = current_user.items_in_cart
        for c in cart:
            item = {}
            item['identifier'] = c.identifier
            item['db'] = c.database
            item['smile'] = c.compound_img
            supplier = []
            for v in c.vendors:
                vendor = {}
                vendor['cat_name'] = v.cat_name
                vendor['supplier_code'] = v.supplier_code
                vendor['quantity'] = v.pack_quantity
                vendor['unit'] = v.unit
                vendor['price'] = v.price
                vendor['purchase'] = v.purchase_quantity
                vendor['shipping'] = v.shipping_str
                supplier.append(vendor)
            item['supplier'] = supplier
            response.append(item)
    return response
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