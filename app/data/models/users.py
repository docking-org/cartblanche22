from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db,login
from flask_login import UserMixin
import json
from app.data.models.carts import Carts


class Users(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    carts = db.relationship('Carts', backref='user', lazy='dynamic')
    activeCart = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    @property
    def cart_count(self):
        return Carts.query.get(self.activeCart).items.count()
        
    @property
    def cart_name(self):
        return Carts.query.get(self.activeCart).name

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def get_id(self):
        return self.user_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def setCart(self, cart_id):
        self.activeCart = cart_id
        db.session.commit()

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))