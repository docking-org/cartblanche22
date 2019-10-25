from flask import render_template, flash, redirect, url_for, jsonify, request
from app.main import bp
from app.forms import LoginForm
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app.models import Users, Carts, Items, Vendors
from app import db
from app.forms import RegistrationForm
import json

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
    priceAPI = [{ "supplier_code": "SPC00007", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 10, "quantity": "NA", "cat_name": "sialbb" }, { "supplier_code": "CDS022812|ALDRICH", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 2, "quantity": "NA", "cat_name": "sialbb" }, { "supplier_code": "SPC00007|ALDRICH", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 3, "quantity": "NA", "cat_name": "sialbb" }, { "supplier_code": "CDS022812", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 32, "quantity": "NA", "cat_name": "sialbb" }, { "supplier_code": "G-6295", "zinc_id": "ZINC000012384497", "cat_id_fk": 24, "price": "NA", "quantity": "NA", "cat_name": "achemblock" }, { "supplier_code": "4003585", "zinc_id": "ZINC000012384497", "cat_id_fk": 32, "price": "NA", "quantity": "NA", "cat_name": "chbre" }, { "supplier_code": "4003585", "zinc_id": "ZINC000012384497", "cat_id_fk": 36, "price": "NA", "quantity": "NA", "cat_name": "chbrbbe" }, { "supplier_code": "QB-9979", "zinc_id": "ZINC000012384497", "cat_id_fk": 58, "price": "NA", "quantity": "NA", "cat_name": "combiblocksbb" }, { "supplier_code": "SPC-a026", "zinc_id": "ZINC000012384497", "cat_id_fk": 60, "price": "110", "quantity": "0.25", "cat_name": "spiro" }, { "supplier_code": "32796", "zinc_id": "ZINC000012384497", "cat_id_fk": 61, "price": "NA", "quantity": "NA", "cat_name": "astateche" }, { "supplier_code": "4H56-1-789", "zinc_id": "ZINC000012384497", "cat_id_fk": 62, "price": "NA", "quantity": "NA", "cat_name": "synquestbb" }]
    for i in priceAPI:
        vendor = Vendors.query.filter_by(item_fk=item_id, supplier_code=i['supplier_code']).first()
        if vendor is None:
            i['buyAmount'] = 0
        else:
            i['buyAmount'] = vendor.quantity
    return jsonify(priceAPI)

@bp.route('/vendorUpdate', methods= ['GET',  'POST'])
def vendorUpdate():
    item_id = request.args.get('item_id')
    value = request.args.get('value')
    datas = request.args.get('data').split(',')
    supplier_code = datas[0]
    company_name = datas[1]
    price = datas[2]
    cat_id_fk = datas[3]
    print(f'{item_id}-{supplier_code}-{value}-{company_name}-{price}-{cat_id_fk}')
    vendor = Vendors.query.filter_by(item_fk=item_id, supplier_code=supplier_code).first()
    if vendor is None and int(value) != 0:
        vendor = Vendors(item_fk=item_id, company_name=company_name, quantity=value,
                            supplier_code=supplier_code, price=price, cat_id_fk=cat_id_fk)
        db.session.add(vendor)
        db.session.commit()
        print(f'added as a vendor : {vendor}')
    elif int(value) == 0:
        Vendors.query.filter_by(item_fk=item_id, supplier_code=supplier_code).delete()
        db.session.commit()
        print(f'vendor deleted')
    else:
        vendor.quantity = int(value)
        db.session.commit()
    return jsonify('post called')  

@bp.route('/cart', methods= ['GET',  'POST'])
def cart():
    data = current_user.cart_fk.getCart()
    # print(type(data))
    return render_template('table.html', data=data)

