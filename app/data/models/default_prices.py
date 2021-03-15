from app import db
from datetime import datetime


class DefaultPrices(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'default_prices'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120), index=True)
    quantity = db.Column(db.Float, default=10)
    unit = db.Column(db.String(10), default='mg')
    price = db.Column(db.Float)
    organization = db.Column(db.String(120), index=True)
    shipping = db.Column(db.String(120), index=True, default='6 weeks')
    created_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()