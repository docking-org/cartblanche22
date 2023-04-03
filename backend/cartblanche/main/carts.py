from flask import render_template, url_for, jsonify, request, make_response
from cartblanche.app import app 
from flask_login import current_user
from cartblanche.data.models.carts import Carts
from cartblanche.data.models.items import Items
from cartblanche.data.models.vendors import Vendors

from cartblanche.data.models.users import Users
from cartblanche.data.models.default_prices import DefaultPrices
from cartblanche.helpers.common import find_molecule, getRole
from cartblanche.app import db
import json
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cartblanche.helpers.validation import identify_dataset
from pandas import DataFrame

@app.route('/cart/getCart', methods=['GET',  'POST'])
@jwt_required(optional=True)
def cart():
    user_id = get_jwt_identity()
 
    current_user = Users.query.filter_by(id=user_id).first()
    cart = Carts.query.filter_by(cart_id=current_user.activeCart).first()
    if cart:
        items = []
        for i in cart.items:
            item = {
                'identifier' : i.identifier,
                'smile' : i.compound_img,
                'db' : i.database,
                'vendors' : []
            }
            for v in i.vendors:
                vendor = {
                    'cat_name' : v.cat_name,
                    'supplier_code' : v.supplier_code,
                    'quantity' : v.pack_quantity,
                    'unit' : v.unit,
                    'price' : v.price,
                    'shipping' : v.shipping_str,
                    'purchase' : v.purchase_quantity,
                    'assigned' : True
                }
                item['vendors'].append(vendor)
            items.append(item)
        res = {
            'name' : cart.name,
            'qty' : cart.count,
            'total' : cart.totalPrice,
            'status' : cart.status,
            'items': items
        }
        return make_response(jsonify(res), 200)
    else:
        return make_response(jsonify({'msg': 'No cart found'}), 200)

@app.route('/carts', methods= ['GET',  'POST'])
@jwt_required()
def carts():
    user_id = get_jwt_identity()
    current_user = Users.query.filter_by(id=user_id).first()
    carts = Carts.query.filter_by(user_fk=user_id).all()
    
    result = []
    for c in carts:
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
    
    return make_response(jsonify(result), 200)

@app.route('/cart/addItems', methods=['POST'])
@jwt_required()
def addItem():
    missingMols = []
    user_id = get_jwt_identity()
    current_user = Users.query.filter_by(id=user_id).first()
    req = request.form
    
    items = (req['items'])
    items = json.loads(items)
    
    for item in items:
        if item.get('identifier'):
            id = item['identifier']
        else:
            id = item['zinc_id']

        found = Items.query.filter_by(identifier=id, cart_fk=current_user.activeCart).first()
        
        if not found:
            new_item = Items(cart_fk=current_user.activeCart, identifier=id, compound_img=item['smiles'],
                            database=item['db'])
            db.session.add(new_item)
            db.session.commit()
            lowest_price = 999999
            best_catalog = None
            for s in item['catalogs']:
                #find catalog with lowest price
                if s.get('price'):
                    if s['price'] < lowest_price:
                        lowest_price = s['price']
                        best_catalog = s
            if best_catalog:
                vendor = Vendors(item_fk=new_item.item_id, cat_name=best_catalog['catalog_name'],
                                purchase_quantity=1,
                                supplier_code=best_catalog['supplier_code'], price=float(best_catalog['price']),
                                pack_quantity=float(best_catalog['quantity']), unit=best_catalog['unit'], shipping_str=best_catalog['shipping'])
                db.session.add(vendor)
                db.session.commit()
            else:
                missingMols.append(id)

    if missingMols:
        if len(items) ==  1:
            return {'msg': "Successfully added {x} item to cart, but {y} item was not found in any catalogs".format(x=len(items), y=len(missingMols))}, 207
        else:
            return {'msg': "Successfully added {x} item(s) to cart, but {y} item(s) were not found in any catalogs".format(x=len(items), y=len(missingMols))}, 207
    else:
        return {'msg': "Successfully added {x} item(s) to cart".format(x=len(items))}, 200
        
         
@app.route('/cart/removeItem', methods=['POST'])
@jwt_required()
def removeItem():
    user_id = get_jwt_identity()
    current_user = Users.query.filter_by(id=user_id).first()
    req = request.form
    items = req['items']
    items = json.loads(items)
    
    for item in items:
        if isinstance(item, str):
            id = item
        elif item.get('identifier'):
            id = item['identifier']
        else:
            id = item['zinc_id']
    
        found = Items.query.filter_by(identifier=id, cart_fk=current_user.activeCart).first()
        if found:
            found.deleteItem()
    return {'msg': "Successfully removed {x} item(s) from cart".format(x=len(items))}, 200

    
@app.route('/clearCart', methods=['POST'])
@jwt_required()
def clearCart():
    user_id = get_jwt_identity()
    current_user = Users.query.filter_by(id=user_id).first()
    cart = Carts.query.filter_by(cart_id=current_user.activeCart).first()
    items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
    if cart:
        for item in items:
            item.deleteItem()
        
        db.session.commit()

        return jsonify('successfully deleted cart'), 200
    else:
        return jsonify('cart not found'), 404

@app.route('/cart/activate', methods=['POST'])
@jwt_required()
def activateCart():
    user_id = get_jwt_identity()
    cart_id = request.form.get('id')
    print(cart_id)
    current_user = Users.query.filter_by(id=user_id).first()
    
    cart = Carts.query.filter_by(cart_id=cart_id).first()
    
    if cart:
        current_user.activeCart = cart_id
        db.session.commit()
        return {'msg': "Successfully activated cart"}, 200
    else:
        return {'msg': "Cart not found"}, 404


@app.route('/cart/create', methods=['POST'])
@jwt_required()
def createCart():
    user_id = get_jwt_identity()
    cart_name = request.form.get('name')
    
    current_user = Users.query.filter_by(id=user_id).first()
    
    new_cart = Carts(user_fk=current_user.id, name=cart_name)

    
    db.session.add(new_cart)
    db.session.commit()
    current_user.activeCart = new_cart.cart_id  
    db.session.commit()
    return {'msg': "Successfully created cart"}, 200

@app.route('/cart/delete', methods=['POST'])
@jwt_required()
def deleteCart():
    user_id = get_jwt_identity()
    cart_id = request.form.get('id')
    cart = Carts.query.filter_by(cart_id=cart_id).first()
    user = Users.query.filter_by(id=user_id).first()
    if cart:
        cart.deleteCart()
        db.session.commit()
        carts = Carts.query.filter_by(user_fk=user_id).all()
        if carts:
            user.activeCart = carts[0].cart_id
            db.session.commit()
        else:
            new = Carts(user_fk=user_id, name="Default")
            db.session.add(new)
            db.session.commit()
        return {'msg': "Successfully deleted cart"}, 200
    else:
        return {'msg': "Cart not found"}, 404
    
    
@app.route('/cart/download', methods=['POST'])
@jwt_required()
def downloadCart():
    user_id = get_jwt_identity()
    format = request.form.get('format')

    current_user = Users.query.filter_by(id=user_id).first()
    cart = Carts.query.filter_by(cart_id=current_user.activeCart).first()
    items = []
    if cart:
        for i in cart.items:
            item = {
                'identifier' : i.identifier,
                'smile' : i.compound_img,
                'db' : i.database,
             
            }
            
            for v in i.vendors:

                item['catalog_name'] = v.cat_name
                item['suppier_code'] = v.supplier_code
                item['quantity'] = v.pack_quantity
                item['unit'] = v.unit
                item['price'] = v.price
                item['shipping'] = v.shipping_str
                item['purchase'] = v.purchase_quantity

                
            items.append(item)
        if format == 'csv' :
            
            res = DataFrame(items)
            res = res.to_csv(encoding='utf-8', index=False, sep=",", line_terminator='\n')
            return make_response(res, 200)
        elif format == 'json':
            return make_response(jsonify(items), 200)
        elif format == 'tsv':
            res = DataFrame(items)
            res = res.to_csv(encoding='utf-8', index=False, sep="\t", line_terminator='\n')
            return make_response(res, 200)



@app.route('/cart/findAndAdd', methods=["POST"])
@jwt_required()
def findAndAdd(database = None):
    identifier = request.form.get('identifier')
    smiles = request.form.get('smiles')
    database = request.form.get('db')
    org = getRole()

    user_id = get_jwt_identity()
    current_user = Users.query.filter_by(id=user_id).first()
    cart = Carts.query.filter_by(cart_id=current_user.activeCart).first()

    

    # if not part of sw datasets, check if it is a zinc id
    found = Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first()

    if found:
        return {'msg': "The item was already in your cart"}, 207

    dataset = identify_dataset(identifier)
    price = DefaultPrices.query.filter_by(
        category_name=dataset, organization=org).first()
    item = None
    
    if price:
        item = {}
        item['identifier'] = identifier
        item['smiles'] = smiles
        item['db'] = database
        item['catalogs'] = [{
            'assigned': True,
            'catalog_name': price.category_name,
            'price': price.price,
            'purchase': 1,
            'quantity': price.quantity,
            'shipping': price.shipping,
            'supplier_code': price.short_name,
            'unit': price.unit
        }]
    else:
        item = find_molecule(identifier, db=database, smiles=smiles)
    

    if not item:
        new_item = Items(cart_fk=current_user.activeCart, identifier=identifier, compound_img=None,
                        database=database)
       
        db.session.add(new_item)
        db.session.commit()

        return {'msg': "The item was not found in any catalog, but was added to the cart anyway"}, 207
    else:     
        
        new_item = Items(cart_fk=current_user.activeCart, identifier=identifier, compound_img=item['smiles'],
                        database=database)
        db.session.add(new_item)
        db.session.commit()   
        lowest_price = 999999
        best_catalog = None
        missingMols = []
        for s in item['catalogs']:
                #find catalog with lowest price
                if s.get('price'):
                    if s['price'] < lowest_price:
                        lowest_price = s['price']
                        best_catalog = s
        if best_catalog:
            vendor = Vendors(item_fk=new_item.item_id, cat_name=best_catalog['catalog_name'],
                            purchase_quantity=1,
                            supplier_code=best_catalog['supplier_code'], price=float(best_catalog['price']),
                            pack_quantity=float(best_catalog['quantity']), unit=best_catalog['unit'], shipping_str=best_catalog['shipping'])
            db.session.add(vendor)
            db.session.commit()
        else:
                
            missingMols.append(id)

        if len(missingMols) == 0:
            return {'msg': "Successfully added {id} to cart".format(id=identifier)}, 200
        elif len(missingMols) == 1:
            return {'msg': "Successfully added {x} item to cart, but {y} item was not found in any catalogs".format(x=len(missingMols), y=len(missingMols))}, 207
        else:
            return {'msg': "Successfully added {x} item(s) to cart, but {y} item(s) were not found in any catalogs".format(x=len(missingMols), y=len(missingMols))}, 207
        
        



@app.route('/cart/getPurchasability', methods=["POST"])
@jwt_required(optional=True)
def getPurchasability(database = None):
    identifier = request.form.get('identifier')
    smiles = request.form.get('smiles')
    database = request.form.get('db')
    org = getRole()

    user_id = get_jwt_identity()
    
    # if not part of sw datasets, check if it is a zinc id

    dataset = identify_dataset(identifier)
    price = DefaultPrices.query.filter_by(
        category_name=dataset, organization=org).first()
    
    item = {}
   
   
    if not price:
   
        item = find_molecule(identifier=identifier, smiles=smiles, db=database)
    else:
        item['identifier'] = identifier
        item['smiles'] = smiles
        item['db'] = database
        item['catalogs'] = [{
            'assigned': True,
            'catalog_name': price.category_name,
            'price': price.price,
            'purchase': 1,
            'quantity': price.quantity,
            'shipping': price.shipping,
            'supplier_code': price.short_name,
            'unit': price.unit
        }]
  
    return make_response(jsonify(item), 200)
 
    
# @app.route("/cart/addAllItem", methods=['POST'])
# def addAllItem():
#     data = request.get_json()['data']
#     for item in data:
#         found = Items.query.filter_by(identifier=item['identifier'], cart_fk=current_user.activeCart).first()
#         if not found:
#             print('adding item:  ', item)
#             new_item = Items(cart_fk=current_user.activeCart, identifier=item['identifier'], compound_img=item['smile'],
#                              database=item['db'])
#             db.session.add(new_item)
#             db.session.commit()
#             for s in item['supplier']:
#                 if s['assigned']:
#                     vendor = Vendors(item_fk=new_item.item_id, cat_name=s['cat_name'],
#                                      purchase_quantity=s['purchase'],
#                                      supplier_code=s['supplier_code'], price=float(s['price']),
#                                      pack_quantity=float(s['quantity']), unit=s['unit'], shipping_str=s['shipping'])
#                     db.session.add(vendor)
#                     db.session.commit()
#                     print('add vendor for new item')
#     return jsonify('successfully added item to cart db')





# @app.route('/addVendorTest', methods=['POST'])
# def addVendorTest():
#     if current_user.is_authenticated:
#         data = request.get_json()['data']
#         identifier = data['identifier']
#         sup = data['sup']
#         item = Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first()
#         vendor = Vendors(item_fk=item.item_id, cat_name=sup['cat_name'],
#                          purchase_quantity=sup['purchase'],
#                          supplier_code=sup['supplier_code'], price=float(sup['price']),
#                          pack_quantity=float(sup['quantity']), unit=sup['unit'], shipping_str=sup['shipping'])
#         db.session.add(vendor)
#         db.session.commit()
#         print('adding vendor:  ', vendor)
#         return jsonify('successfully added vendor to db')
#     return jsonify("user not logged in")


# @app.route('/deleteItemTest', methods=['DELETE'])
# def deleteItemTest():
#     if current_user.is_authenticated:
#         data = request.get_json()['data']
#         identifier = data['identifier']
#         Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first().deleteItem()
#         return jsonify('successfully deleted an item from db')
#     return jsonify("user not logged in")


# @app.route('/deleteMultItem', methods=['DELETE'])
# def deleteMultItem():
#     if current_user.is_authenticated:
#         identifiers = request.get_json()['data']
#         for identifier in identifiers:
#             Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first().deleteItem()
#         return jsonify('successfully deleted an item from db')
#     return jsonify("user not logged in")


# @app.route('/deleteVendorTest', methods=['POST'])
# def deleteVendorTest():
#     if current_user.is_authenticated:
#         data = request.get_json()['data']
#         item = Items.query.filter_by(identifier=data['identifier'], cart_fk=current_user.activeCart).first()
#         vendors = Vendors.query.filter_by(item_fk=item.item_id).all()
#         if len(vendors) <= 1:
#             item.deleteItem()
#         else:
#             vendor = Vendors.query.filter_by(item_fk=item.item_id, cat_name=data['cat_name'],
#                                              supplier_code=data['supplier_code'], price=float(data['price']),
#                                              pack_quantity=float(data['quantity']), unit=data['unit']).first()
#             vendor.deleteVendor()
#         return jsonify('successfully deleted vendor from db')
#     return jsonify("user not logged in")


# @app.route('/updateVendorTest', methods=['POST'])
# def updateVendorTest():
#     if current_user.is_authenticated:
#         data = request.get_json()['data']
#         identifier = data['identifier']
#         item = Items.query.filter_by(identifier=identifier, cart_fk=current_user.activeCart).first()
#         vendor = Vendors.query.filter_by(item_fk=item.item_id, cat_name=data['cat_name'],
#                                          supplier_code=data['supplier_code'], price=float(data['price']),
#                                          pack_quantity=float(data['quantity']), unit=data['unit']).first()
#         print('before',vendor)
#         vendor.updatePurchaseQuantity(data['purchase'])
#         print('after',vendor)
#     return jsonify('successfully updated vendor purchase to db')


# @app.route('/saveCartToDbTest', methods=['POST'])
# def saveCartToDbTest():
#     print('saveCartToDB')
#     data = request.get_json()['totalCart']
#     print(data)
#     for d in data:
#         item = Items.query.filter_by(identifier=d['identifier'], cart_fk=current_user.activeCart).first()
#         if item:
#             suppliers = d['supplier']
#             for s in suppliers:
#                 if s['assigned']:
#                     vendor = Vendors.query.filter_by(item_fk=item.item_id).first()
#                     vendor.deleteVendor()
#                     vendor = Vendors(item_fk=item.item_id, cat_name=s['cat_name'],
#                                          purchase_quantity=s['purchase'],
#                                          supplier_code=s['supplier_code'], price=float(s['price']),
#                                          pack_quantity=float(s['quantity']), unit=s['unit'], shipping_str=s['shipping'])
#                     db.session.add(vendor)
#                     db.session.commit()
#         else:
#             new_item = Items(cart_fk=current_user.activeCart, identifier=d['identifier'], compound_img=d['smile'],
#                              database=d['db'])
#             db.session.add(new_item)
#             db.session.commit()
#             print('add item: ', d['identifier'])
#             print('new_item: ',new_item)
#             suppliers = d['supplier']
#             for s in suppliers:
#                 if s['assigned']:
#                     vendor = Vendors(item_fk=new_item.item_id, cat_name=s['cat_name'],
#                                  purchase_quantity=s['purchase'],
#                                  supplier_code=s['supplier_code'], price=float(s['price']),
#                                  pack_quantity=float(s['quantity']), unit=s['unit'], shipping_str=s['shipping'])
#                     db.session.add(vendor)
#                     db.session.commit()
#                     print('add vendor for new item', vendor.purchase_quantity)
#     response = populateCart()
#     vendor_prices = {}
#     org = 'public'
#     if current_user.is_authenticated and current_user.has_roles('ucsf'):
#         org = 'ucsf'
#     default_prices = DefaultPrices.query.filter_by(organization=org).all()
#     for d in default_prices:
#         vendor = {}
#         vendor['cat_name'] = d.category_name
#         vendor['supplier_code'] = d.category_name
#         vendor['quantity'] = d.quantity
#         vendor['unit'] = d.unit
#         vendor['price'] = d.price
#         vendor['shipping'] = d.shipping
#         vendor['organization'] = d.organization
#         vendor['assigned'] = False
#         vendor['purchase'] = 1
#         vendor_prices[d.short_name] = vendor
#     data = {}
#     data['default_prices'] = vendor_prices
#     data['cart'] = response
#     print('zulaa cart', response)
#     return jsonify(data)




# @app.route('/createCart', methods= ['GET'])
# def createCart():
#     Carts.createCart(current_user)
#     return jsonify(url_for('main.carts'))

# @app.route('/renameCart', methods= ['POST'])
# def renameCart():
#     data = request.get_json()
#     print(data['name'])
#     Carts.query.get(data['cart_id']).setName(data['name'])
#     return jsonify('Cart name successfully updated')

# @app.route('/deleteCart/<cart_id>', methods= ['DELETE'])
# def deleteCart(cart_id):
#     Carts.query.get(cart_id).deleteCart()
#     print('cart deleted')
#     return jsonify('success')

# @app.route('/activateCart/<cart_id>', methods= ['GET'])
# def activateCart(cart_id):
#     print(cart_id)
#     current_user.setCart(cart_id)
#     response = populateCart()
#     vendor_prices = {}
#     org = 'public'
#     if current_user.is_authenticated and current_user.has_roles('ucsf'):
#         org = 'ucsf'
#     default_prices = DefaultPrices.query.filter_by(organization=org).all()
#     for d in default_prices:
#         vendor = {}
#         vendor['cat_name'] = d.category_name
#         vendor['supplier_code'] = d.category_name
#         vendor['quantity'] = d.quantity
#         vendor['unit'] = d.unit
#         vendor['price'] = d.price
#         vendor['shipping'] = d.shipping
#         vendor['organization'] = d.organization
#         vendor['assigned'] = False
#         vendor['purchase'] = 1
#         vendor_prices[d.category_name] = vendor
#     data = {}
#     data['default_prices'] = vendor_prices
#     data['cart'] = response
#     print(vendor_prices)
#     print(data)
#     return jsonify(data)

# def populateCart():
#     response = []
#     if current_user.is_authenticated:
#         cart = current_user.items_in_cart
#         for c in cart:
#             item = {}
#             item['identifier'] = c.identifier
#             item['db'] = c.database
#             item['smile'] = c.compound_img
#             supplier = []
#             for v in c.vendors:
#                 vendor = {}
#                 vendor['cat_name'] = v.cat_name
#                 vendor['supplier_code'] = v.supplier_code
#                 vendor['quantity'] = v.pack_quantity
#                 vendor['unit'] = v.unit
#                 vendor['price'] = v.price
#                 vendor['purchase'] = v.purchase_quantity
#                 vendor['shipping'] = v.shipping_str
#                 vendor['assigned'] = True
#                 supplier.append(vendor)
#             item['supplier'] = supplier
#             response.append(item)
#     return response
# @app.route('/importData', methods=['GET', 'POST'])
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