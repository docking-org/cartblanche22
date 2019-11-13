from app import db

class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    cart_fk = db.Column(db.Integer, db.ForeignKey('carts.cart_id'))
    identifier = db.Column(db.String(120), index=True)
    quantity = db.Column(db.Float, default=10)
    unit = db.Column(db.String(10), default='mg')
    compound_img = db.Column(db.String(256))
    database = db.Column(db.String(120), nullable = False)
    price = db.Column(db.Float)
    vendors = db.relationship('Vendors', backref='item', lazy='dynamic')

    # def __repr__(self):
    #     data = {'item_id':self.item_id,'identifier':self.identifier, 'quantity':self.quantity, 
    #             'unit':self.unit, 'compound_img':self.compound_img, 
    #             'database':self.database, 'price':self.price, 'vendors':self.vendors
    #             }
    #     return json.dumps(data)
    
    def deleteItem(item_id):
        Items.query.filter_by(item_id=item_id).delete()
        db.session.commit()
        print('item deleted')
