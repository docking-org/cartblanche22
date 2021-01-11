from app import db
import datetime

class TrancheModel(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'tranche'

    tranche_id = db.Column('tranche_id', db.Integer, nullable=False, primary_key=True)
    mwt = db.Column('mwt', db.CHAR(1), nullable=False)
    logp = db.Column('logp', db.CHAR(1), nullable=False)

    sum  = db.Column('sum', db.Integer, nullable=True, default=0)
    last = db.Column('last', db.Date, nullable=True, default=datetime.datetime.today)

    h_num = db.Column('h_num', db.String(64), nullable=True, default=0)
    p_num = db.Column('p_num', db.String(64), nullable=True, default=0)

    charge = db.Column('charge', db.CHAR(1), nullable=False)

    server_mapping_fk = db.Column(db.Integer, db.ForeignKey('server_mapping.sm_id'), nullable=False)
    server_mapping = db.relationship('ServerMappingModel', backref='tranches')

    def to_dict(self):
        return {
            'tranche_id': self.tranche_id,
            'mwt': self.mwt, 
            'logp': self.logp, 
            'h_num': self.h_num, 
            'p_num': self.p_num
        }

    
    def url_string(self):
        if self.server_mapping:
            return "{}:{}".format(self.server_mapping.ip_address.ip, self.server_mapping.port_number.port)
        else:
            return None

    @classmethod
    def find_by_mwt(cls, mwt):
        return cls.query.filter_by(mwt=mwt).first()

    @classmethod
    def find_by_logp(cls, logp):
        return cls.query.filter_by(hac=logp).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return '<Tranche {}{}{}>'.format(self.tranche_id, self.h_num, self.p_num)