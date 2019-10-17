from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db,login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cart = db.relationship("Cart", uselist=False, back_populates="user")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="cart")
    items = db.relationship('Item', backref='cart', lazy='dynamic')

    def __repr__(self):
        return f'<Cart {self.id} {self.user_id}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    zinc_id = db.Column(db.String(120), index=True)

    def __repr__(self):
        return f'<Item {self.zinc_id} {self.cart_id}>'


