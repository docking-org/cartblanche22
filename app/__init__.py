from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_user import UserManager
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login = LoginManager()
bootstrap = Bootstrap()
mail = Mail()


def create_app(config_class=Config):
    application = app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login.init_app(app)
    login.login_view = 'main.login'

    mail.init_app(app)

    bootstrap.init_app(app)

    from app.data.models.users import Users
    from app.data.models.roles import Roles
    from app.data.models.carts import Carts
    from app.data.models.items import Items
    from app.data.models.vendors import Vendors
    from app.data.models.availableVendors import AvailableVendors

    admin = Admin(app, name='shoppingcart', template_mode='bootstrap3')
    admin.add_view(ModelView(Users, db.session))
    admin.add_view(ModelView(Roles, db.session))
    admin.add_view(ModelView(Vendors, db.session))
    admin.add_view(ModelView(AvailableVendors, db.session))

    from app.errors import application as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import application as main_bp
    app.register_blueprint(main_bp)
    return app

# from app import models
