from app import db 

class AvailableVendors(db.Model):
    __tablename__ = 'availableVendors'
    vendor_id = db.Column(db.Integer, primary_key=True)
    cat_id_fk = db.Column(db.Integer)
    short_name = db.Column(db.String(120))
    bb = db.Column(db.Boolean)
    purchasable = db.Column(db.Integer)
    name = db.Column(db.String(120))
    availability = db.Column(db.Boolean)
    priority = db.Column(db.Integer, default=50)
    
    def createAvailableVendors(l):
        vendor = AvailableVendors(cat_id_fk=l[0], bb=l[1], short_name=l[2], purchasable=l[3], name=l[4], availability=True)
        db.session.add(vendor)
        db.session.commit()

class UserVendors(db.Model):
    __tablename__ = 'user_vendors'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    vendor_id = db.Column(db.Integer(), db.ForeignKey('availableVendors.vendor_id', ondelete='CASCADE'))
    priority = db.Column(db.Integer(), default=50)

    vendor = db.relationship(AvailableVendors, backref="users")
    user = db.relationship('Users', backref="vendors")

    def delete(self):
        db.session.delete(self)
        db.session.commit()