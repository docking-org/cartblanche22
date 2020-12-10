from app import db

class PortNumberModel(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'port_number'

    port_id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer)
    
    def __init__(self, port):
        self.port = port

    def json(self):
        return {'port_id': self.port_id, 'port': self.port}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return self.ip

    def __repr__(self):
        return '<PortNumber {}>'.format(self.port)