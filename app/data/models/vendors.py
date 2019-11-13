from app import db

class Vendors(db.Model):
    vendor_id = db.Column(db.Integer, primary_key=True)
    item_fk = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    cat_name = db.Column(db.String(120), index=True)
    pack_quantity = db.Column(db.Float, default=0)
    purchase_quantity = db.Column(db.Integer)
    unit = db.Column(db.String(10), default='mg')
    supplier_code = db.Column(db.String(120))
    price = db.Column(db.Float)
    shipping = db.Column(db.Integer)
    currency = db.Column(db.String(10), default="usd")
    cat_id_fk = db.Column(db.Integer)
