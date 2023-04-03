from cartblanche.app import db


class Tranches(db.Model):
    # __bind_key__ = 'tin'
    __tablename__ = 'tranches'

    tranche_id = db.Column(db.Integer, primary_key=True)
    tranche_name = db.Column(db.String)

    def json(self):
        return {'tranche_id': self.tranche_id, 'tranche_name': self.tranche_name}







