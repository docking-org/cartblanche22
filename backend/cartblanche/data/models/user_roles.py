from cartblanche.app import db

class UserRoles(db.Model):
    __bind_key__ = 'zinc22'
    __tablename__ = 'user_roles'
            
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.role_id', ondelete='CASCADE'))