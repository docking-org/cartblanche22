from cartblanche.app import db
from datetime import datetime

class Vendors(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'vendors'

    vendor_id = db.Column(db.Integer, primary_key=True)
    item_fk = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    cat_name = db.Column(db.String(120), index=True)
    pack_quantity = db.Column(db.Float, default=0)
    purchase_quantity = db.Column(db.Integer)
    unit = db.Column(db.String(10), default='mg')
    supplier_code = db.Column(db.String(120))
    price = db.Column(db.Float)
    shipping = db.Column(db.Integer)
    shipping_str = db.Column(db.String(120), default="undefined")
    currency = db.Column(db.String(10), default="usd")
    cat_id_fk = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return 'id: {}, cat_name:{}, supplier_code:{}, pack_quantity:{}, price:{}, purchase_quantity:{}'.format(self.vendor_id, self.cat_name, self.supplier_code, self.pack_quantity, self.price, self.purchase_quantity)

    def updatePurchaseQuantity(self, qty):
        self.purchase_quantity = qty
        db.session.commit()

    def deleteVendor(self):
        db.session.delete(self)
        db.session.commit()

    def createVendor(item, item_id):
        print("creating vendor {} : {}".format(item, item_id))
        vendor = Vendors(item_fk=item_id, cat_name=item['cat_name'], cat_id_fk=item['cat_id_fk'],
                        purchase_quantity=item['purchase_quantity'],
                        supplier_code=item['supplier_code'], price=float(item['price']), 
                        pack_quantity=float(item['quantity']), unit=item['unit'])
        db.session.add(vendor)
        db.session.commit()

    def addVendor(item_id, vendor):
        vendor_ = Vendors.query.filter_by(item_fk=item_id, cat_name=vendor['cat_name'],                   supplier_code=vendor['supplier_code'], price=float(vendor['price']),                   pack_quantity=float(vendor['quantity']), unit=vendor['unit']).first()
        if vendor_:
            vendor_.purchase_quantity = vendor['purchase']
        else:
            vendor_ = Vendors(item_fk=item_id, cat_name=vendor['cat_name'], 
                        purchase_quantity=vendor['purchase'],
                        supplier_code=vendor['supplier_code'], price=float(vendor['price']), 
                        pack_quantity=float(vendor['quantity']), unit=vendor['unit'], shipping_str=vendor['shipping'])
        db.session.add(vendor_)
        db.session.commit()
        return vendor_
