from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db,login
from flask_login import UserMixin
import json
class Users(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cart_fk = db.relationship("Carts", uselist=False, backref="user")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_id(self):
        return self.user_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Carts(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    items = db.relationship('Items', backref='cart', lazy='dynamic')

    def __repr__(self):
        return f'<Cart {self.cart_id}>'
    
    def addToCart(self, data):
        data['cart_id'] = self.cart_id
        Items.createItem(data)
        # print(data)data['id'], data['img_url'], data['database']
    
    def deleteFromCart(item):
        pass
    
    def updateCart(item):
        pass

    def createCart(user):
        cart = Carts(user_fk= user.user_id)
        db.session.add(cart)
        db.session.commit()
        print(f'cart created for {user} with cart {cart}')
    
    def order():
        pass

    def getCart(self):
        return self.items

class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    cart_fk = db.Column(db.Integer, db.ForeignKey('carts.cart_id'))
    identifier = db.Column(db.String(120), index=True)
    quantity = db.Column(db.Integer, default=10)
    unit = db.Column(db.String(10), default='mg')
    compound_img = db.Column(db.String(256))
    database = db.Column(db.String(120), nullable = False)
    price = db.Column(db.Integer)
    vendors = db.relationship('Vendors', backref='item', lazy='dynamic')

    def __repr__(self):
        data = {'item_id':self.item_id,'identifier':self.identifier, 'quantity':self.quantity, 
                'unit':self.unit, 'compound_img':self.compound_img, 
                'database':self.database, 'price':self.price, 'vendors':self.vendors
                }
        return json.dumps(data)
    
    def deleteItem(item_id):
        Items.query.filter_by(item_id=item_id).delete()
        db.session.commit()
        print('item deleted')

    def getItem(self):
        data = {'item_id':self.item_id,'identifier':self.identifier, 'quantity':self.quantity,
                'unit':self.unit, 'compound_img':self.compound_img,
                'database':self.database, 'price':self.price
                }
        return json.dumps(data)

class Vendors(db.Model):
    vendor_id = db.Column(db.Integer, primary_key=True)
    item_fk = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    company_name = db.Column(db.String(120), index=True)
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(10), default='mg')
    supplier_code = db.Column(db.String(120))
    price = db.Column(db.Integer)
    cat_id_fk = db.Column(db.String(120))
    
    def __repr__(self):
        data = {'company_name':self.company_name,'quantity':self.quantity, 'supplier_code':self.supplier_code, 
                'price':self.price
                }
        return json.dumps(data)


def findVendors(id):
    return [{"supplier_code": "SPC00007", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 10, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "CDS022812|ALDRICH", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 2, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "SPC00007|ALDRICH", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 3, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "CDS022812", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 32, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "G-6295", "zinc_id": "ZINC000012384497", "cat_id_fk": 24, "price": "NA", "quantity": "NA", "cat_name": "achemblock"}, {"supplier_code": "4003585", "zinc_id": "ZINC000012384497", "cat_id_fk": 32, "price": "NA", "quantity": "NA", "cat_name": "chbre"}, {"supplier_code": "4003585", "zinc_id": "ZINC000012384497", "cat_id_fk": 36, "price": "NA", "quantity": "NA", "cat_name": "chbrbbe"}, {"supplier_code": "QB-9979", "zinc_id": "ZINC000012384497", "cat_id_fk": 58, "price": "NA", "quantity": "NA", "cat_name": "combiblocksbb"}, {"supplier_code": "SPC-a026", "zinc_id": "ZINC000012384497", "cat_id_fk": 60, "price": "110", "quantity": "0.25 g", "cat_name": "spiro"}, {"supplier_code": "32796", "zinc_id": "ZINC000012384497", "cat_id_fk": 61, "price": "NA", "quantity": "NA", "cat_name": "astateche"}, {"supplier_code": "4H56-1-789", "zinc_id": "ZINC000012384497", "cat_id_fk": 62, "price": "NA", "quantity": "NA", "cat_name": "synquestbb"}]
