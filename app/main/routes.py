from flask import render_template, flash, redirect, url_for, jsonify, request
from app.main import bp
from app.forms import LoginForm
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app.models import Users, Carts, Items
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
    item = Items.query.filter_by(identifier=request.args.get('id')).first()
    if item is None:
        item = Items(cart_fk = current_user.cart_fk.cart_id, identifier=request.args.get('id'), 
                compound_img=request.args.get('img_url'), database= request.args.get('database'))
        db.session.add(item)
        db.session.commit()
        return jsonify('added to cart success')
    return jsonify('item exists in cart')

@bp.route('/deleteItem/<item_id>', methods= ['POST'])
def deleteItem(item_id):
    Items.query.filter_by(item_id=item_id).delete()
    db.session.commit()
    print('item deleted')
    return redirect(url_for('main.cart'))

@bp.route('/vendorModal/<item_id>', methods= ['POST'])
def vendorModal(item_id):
    item = Items.query.get(item_id)
    print(item)
    return redirect(url_for('main.cart'))

@bp.route('/cart', methods= ['GET',  'POST'])
def cart():
    data = current_user.cart_fk.getCart()
    # print(type(data))
    return render_template('table.html', data=data)

