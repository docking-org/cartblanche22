from app import db

class IPAddressModel(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'ip_address'

    ip_id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(80))
    # server_mappings = db.relationship('ServerMappingModel', back_populates='ip_address')
    
    def __init__(self, ip):
        self.ip = ip

    def json(self):
        return {'ip_id': self.ip_id, 'ip': self.ip}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return self.ip

    def __repr__(self):
        return '<IPAddress {}>'.format(self.ip)