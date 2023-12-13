from flask import render_template, flash, redirect, url_for, request, jsonify, session
from cartblanche.app import app 
from flask_login import current_user, login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, create_refresh_token, unset_jwt_cookies, jwt_required, get_jwt_identity, get_jwt
from werkzeug.urls import url_parse
from cartblanche.data.models.users import Users
from cartblanche.data.models.carts import Carts
from cartblanche.app import db
from cartblanche.email_send import send_password_reset_email
from flask import Markup
from time import time

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember')
   
    user = Users.query.filter_by(username=username).first()
    
    if user is None or not user.check_password(password):            
        return {'msg': 'Invalid username or password'}, 401

    access_token = create_access_token(identity=user.id)
    
    return {
            'access_token': access_token, 
            "username": user.username,
            'msg': 'Logged in as {}'.format(user.username)
            }, 200

@app.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    #extend the expiration time of the access token, if token is within 5 minutes of expiring
    inucsf = request.access_route[-1][0:3] == '10.' or  request.access_route[-1][0:8] == '169.230.' or request.access_route[-1][0:8] == '128.218.' or request.access_route[0] == '127.0.0.1'
    current_user = get_jwt_identity()
    exp = get_jwt()['exp']
    if exp - time() < 300:
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token,
                'inucsf': inucsf,
        }, 200

    return {'msg': 'Verified',
            'inucsf': inucsf,
    }, 200


@app.route('/logout', methods=['POST'])
def logout():
    res = jsonify({'msg': 'Successfully logged out'})
    unset_jwt_cookies(res)
    return res, 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if Users.query.filter_by(username=username).first():
        return {'msg': 'Username already exists'}, 400
    if Users.query.filter_by(email=email).first():
        return {'msg': 'That email alreay has an account.'}, 400

    user = Users(username=username, email= email)
    user.set_password(password=password)
   
    Carts.createCart(user)
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    return {'access_token': access_token, "username": user.username}, 200

@app.route('/forgotPassword', methods=['POST'])
def reset_password_request():
    email = request.form.get('email')
    user = Users.query.filter_by(email=email).first()
    if user:
        send_password_reset_email(user)
    return {'msg': 'If your email is linked to an account, an email will be sent to you shortly. Please follow the instructions there to reset your password.'}, 200

@app.route('/reset_password', methods=['POST'])
@app.route('/reset_password/<token>', methods=['POST'])
def reset_password():
    token = request.form.get('token')
    password = request.form.get('password')
    
    user = Users.verify_reset_password_token(token)
    if not user:
        return {'msg': 'Invalid token'}, 400
    
    user.set_password(password)
    db.session.commit()
    unset_jwt_cookies(jsonify({'msg': 'Successfully logged out'}))
    token = create_access_token(identity=user.id)
    
    return {'msg': 'Your password has been reset.', 'access_token': token, "username": user.username}, 200

@app.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    return
    # form = ChangePasswordForm()
    # if form.validate_on_submit() and current_user.is_authenticated:
    #     current_user.set_password(form.password.data)
    #     db.session.commit()
    #     flash('Your password has been changed.')
    #     return redirect(url_for('main.profile'))
    # return render_template('auth/change_password.html', form=form)