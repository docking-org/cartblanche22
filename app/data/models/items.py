from app import db
from app.data.models.vendors import Vendors

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

    def deleteItem(self):
        for vendor in self.vendors:
            vendor.deleteVendor()
        db.session.delete(self)
        db.session.commit()
