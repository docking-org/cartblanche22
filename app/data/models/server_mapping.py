from app import db

class ServerMappingModel(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'server_mapping'

    sm_id = db.Column(db.Integer, primary_key=True)

    ip_fk = db.Column(db.Integer, db.ForeignKey('ip_address.ip_id'), nullable=False)
    ip_address = db.relationship('IPAddressModel',   backref='server_mappings')

    port_fk = db.Column(db.Integer, db.ForeignKey('port_number.port_id'), nullable=False)
    port_number = db.relationship('PortNumberModel', backref='server_mappings')


    def __init__(self, ip_address, port_number):
        self.ip_address = ip_address
        self.ip_fk = ip_address.id
        self.port_number = port_number
        self.port_fk = port.id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()