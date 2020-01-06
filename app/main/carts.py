from flask import render_template, flash, redirect, url_for, jsonify, request, send_file
from app.main import application
from flask_login import current_user
from app.data.models.carts import Carts
from app.data.models.items import Items
import csv, os


@application.route('/cart', methods= ['GET',  'POST'])
def cart():
    items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
    totalPrices=[]
    totalQuantities=[]
    return render_template('cart/cart.html', data=items, prices=totalPrices, quantities=totalQuantities)

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

# @application.route('/cart/excel', methods=["GET"])
# def cartExcelExport():
#     items = Items.query.filter_by(cart_fk=current_user.activeCart).all()
#     totalPrices=[]
#     totalQuantities=[]
#     with open('cart.csv', 'w', newline='') as csvfile:
#         fieldnames = ['identifier', 'company name', 'pack quantity', 'unit', 'price','currency' ,'purchase quantity']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
#         writer.writeheader()
#         for i in items:
#             for v in i.vendors:
#                  writer.writerow({
#                     'identifier': i.identifier, 
#                     'company name': v.cat_name,
#                     'pack quantity': v.pack_quantity,
#                     'unit' : v.unit,
#                     'price' : v.price,
#                     'currency' : v.currency,
#                     'purchase quantity' : v.purchase_quantity
#                     })
#     d = {'identifier':[],'company name': [], 'pack quantity': [],'unit':[], 'price': [],'currency':[], 'purchase quantity':[]}
#     for i in items:
#         for v in i.vendors:
#             d['identifier'].append(i.identifier)
#             d['company name'].append(v.cat_name)
#             d['pack quantity'].append(v.pack_quantity)
#             d['unit'].append(v.unit)
#             d['price'].append(v.price)
#             d['currency'].append(v.currency)
#             d['purchase quantity'].append(v.purchase_quantity)

#     df = pd.DataFrame(data=d)
#     print("Original DataFrame")
#     print(df)
#     print('Data from new_file.csv file:')
#     new_df = df.to_csv('new_file.csv', sep='\t', index=False)
#     new_df = pd.read_csv('new_file.csv')
#     folder =  os.getcwd()
#     file_dr = os.path.realpath(folder)
#     return send_file(folder+ '/cart.csv',
#                      mimetype='text/csv',
#                      attachment_filename='cart.csv',
#                      as_attachment=True)
#     # resp = make_response(new_df)
#     # resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#     # resp.headers["Content-Type"] = "text/csv"
#     # return resp

#     # return send_file(new_df,
#     #                  mimetype='text/csv',
#     #                  attachment_filename='cart.csv',
#     #                  as_attachment=True)
#     return redirect(url_for('main.cart'))