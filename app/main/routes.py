from flask import render_template, flash, redirect, url_for, jsonify, request, send_file
from app.main import bp
from app.forms import LoginForm
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app.models import Users, Carts, Items, Vendors
from app import db
from app.forms import RegistrationForm
import json, csv, os
import pandas as pd
import numpy as np
import urllib.request

@bp.route('/')
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
        #flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        #return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        Carts.createCart(user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/addToCart', methods= ['GET',  'POST'])
def addToCart():
    item = Items.query.filter_by(cart_fk=current_user.cart_fk.cart_id, identifier=request.args.get('id')).first()
    if item is None:
        item = Items(cart_fk = current_user.cart_fk.cart_id, identifier=request.args.get('id'), 
                compound_img=request.args.get('img_url'), database= request.args.get('database'))
        db.session.add(item)
        db.session.commit()
        return jsonify('added to cart success')
    return jsonify('item exists in cart')

@bp.route('/deleteItem/<item_id>', methods= ['POST'])
def deleteItem(item_id):
    Vendors.query.filter_by(item_fk=item_id).delete()
    Items.query.filter_by(item_id=item_id).delete()
    db.session.commit()
    print('item deleted')
    return redirect(url_for('main.cart'))

@bp.route('/vendorModal/<item_id>', methods= ['GET','POST'])
def vendorModal(item_id):
    item = Items.query.get(item_id)
    uri = "http://gimel.compbio.ucsf.edu:5022/api/_get_data?molecule_id=" + item.identifier
    with urllib.request.urlopen(uri) as url:
        data = json.loads(url.read().decode())
    if data:
        priceAPI = []
        for d in data:
            priceAPI.append(d)
        for i in priceAPI:
            for pack in i['packs']:
                vendor = Vendors.query.filter_by(item_fk=item_id, cat_name=i['cat_name'],
                        pack_quantity=float(pack['quantity']), unit=pack['unit']).first()
                if vendor:
                        pack['purchase_quantity'] = vendor.purchase_quantity
                else:
                    pack['purchase_quantity'] = 0
        return jsonify(priceAPI)
    else:
        return jsonify('null')

@bp.route('/vendorUpdate', methods= ['POST'])
def vendorUpdate():
    data = request.get_json()
    # Since user chose new vendors we do not need to store old chosen vendors
    Vendors.query.filter_by(item_fk = data['item_id']).delete()
    for item in data['post_data']:
        vendor = Vendors(item_fk=data['item_id'], cat_name=item['cat_name'], 
                        purchase_quantity=item['purchase_quantity'],
                        supplier_code=item['supplier_code'], price=float(item['price']), 
                        pack_quantity=float(item['quantity']), unit=item['unit'])
        db.session.add(vendor)
        db.session.commit()
    return jsonify('success')

@bp.route('/cart', methods= ['GET',  'POST'])
def cart():
    items = current_user.cart_fk.items
    totalPrices=[]
    totalQuantities=[]
    return render_template('table.html', data=items, prices=totalPrices, quantities=totalQuantities)

@bp.route('/tsv', methods= ['GET',  'POST'])
def tsv():
    items = current_user.cart_fk.items
    totalPrices=[]
    totalQuantities=[]
    with open('cart.csv', 'w', newline='') as csvfile:
        fieldnames = ['identifier', 'company name', 'pack quantity', 'unit', 'price','currency' ,'purchase quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for i in items:
            for v in i.vendors:
                 writer.writerow({
                    'identifier': i.identifier, 
                    'company name': v.company_name,
                    'pack quantity': v.pack_quantity,
                    'unit' : v.unit,
                    'price' : v.price,
                    'currency' : v.currency,
                    'purchase quantity' : v.purchase_quantity
                    })
    # d = {'identifier':[],'company name': [], 'pack quantity': [],'unit':[], 'price': [],'currency':[], 'purchase quantity':[]}
    # for i in items:
    #     for v in i.vendors:
    #         d['identifier'].append(i.identifier)
    #         d['company name'].append(v.company_name)
    #         d['pack quantity'].append(v.pack_quantity)
    #         d['unit'].append(v.unit)
    #         d['price'].append(v.price)
    #         d['currency'].append(v.currency)
    #         d['purchase quantity'].append(v.purchase_quantity)

    # df = pd.DataFrame(data=d)
    # print("Original DataFrame")
    # print(df)
    # print('Data from new_file.csv file:')
    # new_df = df.to_csv('new_file.csv', sep='\t', index=False)
    # new_df = pd.read_csv('new_file.csv')
    folder =  os.getcwd()
    # file_dr = os.path.realpath(folder)
    return send_file(folder+ '/cart.csv',
                     mimetype='text/csv',
                     attachment_filename='cart.csv',
                     as_attachment=True)
    # resp = make_response(new_df)
    # resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    # resp.headers["Content-Type"] = "text/csv"
    # return resp

    # return send_file(new_df,
    #                  mimetype='text/csv',
    #                  attachment_filename='cart.csv',
    #                  as_attachment=True)
    return redirect(url_for('main.cart'))
