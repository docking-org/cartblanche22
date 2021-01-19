from app import db
import enum
import datetime
from app.data.models.items import Items
from datetime import datetime

# class CartStatusEnum(enum.Enum):
#     one = 'Prepare'
#     two = 'Query'
#     three = 'Back from vendor'
#     four = 'Placed'
#     five = 'Partial reciept'
#     six = 'Complete/archived'
#     seven = 'Cancelled'


class Carts(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'carts'

    cart_id = db.Column(db.Integer, primary_key=True)
    user_fk = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('Items', backref='cart', lazy='dynamic')
    name = db.Column(db.String(256), default='Cart')
    status = db.Column(db.String(256))
    created_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Cart {}>'.format(self.cart_id)
    
    def addToCart(self, current_user, identifier, img_url, database):
        item = Items.query.filter_by(cart_fk=current_user.activeCart, identifier=identifier).first()
        if item is None:
            item = Items(cart_fk = current_user.activeCart, identifier=identifier, compound_img=img_url, database=database)
            db.session.add(item)
            db.session.commit() 
            return item.item_id
        return False

    def addToCartGetId(self, current_user, identifier, img_url, database):
        item = Items.query.filter_by(cart_fk=current_user.activeCart, identifier=identifier).first()
        print(item)
        if item is None:
            print(img_url, database)
            item = Items(cart_fk=current_user.activeCart, identifier=identifier, compound_img=img_url, database=database)
            db.session.add(item)
            db.session.commit() 
        return item.item_id

    def deleteCart(self):
        for item in self.items:
            item.deleteItem()
        db.session.delete(self)
        db.session.commit()
    
    def updateCart(item):
        pass

    def createCart(user):
        cart = Carts(user_fk=user.id)
        db.session.add(cart)
        db.session.commit()
        cart.name += str(cart.cart_id)
        db.session.commit()
        user.setCart(cart.cart_id)
        return cart
    
    def order():
        pass

    def getCart(self):
        return self.items
    
    def setName(self, name):
        self.name = name
        db.session.commit()
    
    @property
    def count(self):
        return self.items.count()

    @property
    def price(self):
        price = 0
        for i in self.items:
            price += 0
        return price
    @property
    def totalPrice(self):
        total = 0
        for i in self.items:
            total += i.totalPrice
        return total
