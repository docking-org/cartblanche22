from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db,login
from flask_login import UserMixin
import json
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cart = db.relationship("Cart", uselist=False, backref="user")

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
    items = db.relationship('Item', backref='cart', lazy='dynamic')

    def __repr__(self):
        return f'<Cart {self.id}>'
    
    def addToCart(self, data):
        data['cart_id'] = self.id
        Item.createItem(data)
        # print(data)data['id'], data['img_url'], data['database']
    
    def deleteFromCart(item):
        pass
    
    def updateCart(item):
        pass

    def createCart(user):
        cart = Cart(user_id= user.id)
        db.session.add(cart)
        db.session.commit()
        print(f'cart created for {user} with cart {cart}')
    
    def order():
        pass

    def getCart(self):
        # data = []
        # for i in self.items:
        #     data.append(i.getItem())
        # return json.dumps(data)
        return self.items

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    identifier = db.Column(db.String(120), index=True)
    quantity = db.Column(db.Integer, default=10)
    unit = db.Column(db.String(10), default='mg')
    compound_img = db.Column(db.String(256))
    database = db.Column(db.String(120), nullable = False)
    company_name = db.Column(db.String(120))
    delivery_time = db.Column(db.String(120))
    price = db.Column(db.Integer)
    supplier_code = db.Column(db.String(120))
    cat_id_fk = db.Column(db.String(120))

    def __repr__(self):
        # return f'<Item {self.identifier} {self.quantity}{self.unit} from {self.database} database...Vendor is {self.company_name} with {self.price} $>'
        data = {'id':self.id,'identifier':self.identifier, 'quantity':self.quantity, 
                'unit':self.unit, 'compound_img':self.compound_img, 
                'database':self.database, 'company_name':self.company_name,
                'delivery_time':self.delivery_time, 'price':self.price,
                'supplier_code':self.supplier_code, 'cat_id_fk':self.cat_id_fk
                }
        return json.dumps(data)

    def createItem(data):
        item = Item(cart_id = data['cart_id'], identifier=data['id'], 
                    compound_img=data['img_url'], database= data['database'])
        db.session.add(item)
        db.session.commit()
        data['item_id'] = item.id
        print(f'item created {item}')

    def getItem(self):
        data = {'identifier':self.identifier, 'quantity':self.quantity, 
                'unit':self.unit, 'compound_img':self.compound_img, 
                'database':self.database, 'company_name':self.company_name,
                'delivery_time':self.delivery_time, 'price':self.price,
                'supplier_code':self.supplier_code, 'cat_id_fk':self.cat_id_fk
                }
        return json.dumps(data)
        
def findVendors(id):
    return [{"supplier_code": "SPC00007", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 10, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "CDS022812|ALDRICH", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 2, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "SPC00007|ALDRICH", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 3, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "CDS022812", "zinc_id": "ZINC000012384497", "cat_id_fk": 6, "price": 32, "quantity": "NA", "cat_name": "sialbb"}, {"supplier_code": "G-6295", "zinc_id": "ZINC000012384497", "cat_id_fk": 24, "price": "NA", "quantity": "NA", "cat_name": "achemblock"}, {"supplier_code": "4003585", "zinc_id": "ZINC000012384497", "cat_id_fk": 32, "price": "NA", "quantity": "NA", "cat_name": "chbre"}, {"supplier_code": "4003585", "zinc_id": "ZINC000012384497", "cat_id_fk": 36, "price": "NA", "quantity": "NA", "cat_name": "chbrbbe"}, {"supplier_code": "QB-9979", "zinc_id": "ZINC000012384497", "cat_id_fk": 58, "price": "NA", "quantity": "NA", "cat_name": "combiblocksbb"}, {"supplier_code": "SPC-a026", "zinc_id": "ZINC000012384497", "cat_id_fk": 60, "price": "110", "quantity": "0.25 g", "cat_name": "spiro"}, {"supplier_code": "32796", "zinc_id": "ZINC000012384497", "cat_id_fk": 61, "price": "NA", "quantity": "NA", "cat_name": "astateche"}, {"supplier_code": "4H56-1-789", "zinc_id": "ZINC000012384497", "cat_id_fk": 62, "price": "NA", "quantity": "NA", "cat_name": "synquestbb"}]
