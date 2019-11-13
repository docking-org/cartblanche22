from app import db

class Carts(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    items = db.relationship('Items', backref='cart', lazy='dynamic')

    def __repr__(self):
        return '<Cart {}>'.format(self.cart_id)
    
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
        
    
    def order():
        pass

    def getCart(self):
        return self.items