from app import db

class Tranche(db.Model):
    tranche_id = db.Column(db.Integer, primary_key=True)
    mwt = db.Column(db.String(64))
    logp = db.Column(db.String(64))
    h_num = db.Column(db.String(64))
    p_num = db.Column(db.String(64))
    sum = db.Column(db.Integer)
    last = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Tranche {}{}{}>'.format(self.tranche_id, self.h_num, self.p_num)