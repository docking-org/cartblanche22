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
from flask_restful import Api
from flask_cors import CORS 

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login = LoginManager()
bootstrap = Bootstrap()
mail = Mail()
api = Api()
cors = CORS()


def create_app(config_class=Config):
    application = app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'zinc22': 'postgresql+psycopg2://test:@mem2.cluster.ucsf.bkslab.org:5432/zinc22',
        # 'zinc22': 'postgresql+psycopg2://test:@localhost:6533/zinc22',
        'tin': 'postgresql+psycopg2://tinuser:usertin@' + app.config['TIN_URL'] + '/tin'
    }


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


    from app.data.models.port_number import PortNumberModel
    from app.data.models.ip_address import IPAddressModel
    from app.data.models.server_mapping import ServerMappingModel
    from app.data.models.tin.substance import SubstanceModel
    from app.data.models.tin.catalog import CatalogModel, CatalogContentModel, CatalogSubstanceModel, CatalogModel
    
    from app.data.resources.main import Search
    from app.data.resources.substance import Substance, Substances, SubstanceList
    from app.data.resources.catalog_content import CatalogContents, CatalogContent
    from app.data.resources.tranche import Tranches

    admin = Admin(app, name='shoppingcart', template_mode='bootstrap3')
    admin.add_view(ModelView(Users, db.session))
    admin.add_view(ModelView(Roles, db.session))
    admin.add_view(ModelView(Vendors, db.session))
    admin.add_view(ModelView(AvailableVendors, db.session))


    api.add_resource(Search, '/search.<file_type>')
    api.add_resource(Substance, '/substance')
    api.add_resource(Substances, '/substances.<file_type>')
    api.add_resource(SubstanceList, '/sublist')
    api.add_resource(CatalogContent, '/catalog')
    api.add_resource(CatalogContents, '/catalogs.<file_type>')
    api.add_resource(Tranches, '/tranches.<file_type>')

    from app.errors import application as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import application as main_bp
    app.register_blueprint(main_bp)

    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    cors.init_app(app)

    return app

# from app import models
