from cartblanche.app import db


class Roles(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'roles'

    role_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

