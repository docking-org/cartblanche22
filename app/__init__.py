from flask import Flask, g, current_app, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_user import UserManager
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from flask_restful import Api
from flask_cors import CORS
from flask_restful import reqparse


class MultiTenantSQLAlchemy(SQLAlchemy):
    def choose_tenant(self, bind_key):
        if hasattr(g, 'tenant'):
            raise RuntimeError('Switching tenant in the middle of the request.')
        g.tenant = bind_key

    def get_engine(self, app=None, bind=None):
        if bind is None:
            if not hasattr(g, 'tenant'):
                raise RuntimeError('No tenant chosen.')
            bind = g.tenant
        return super().get_engine(app=app, bind=bind)


db = MultiTenantSQLAlchemy()
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
        # 'zinc22': 'postgresql+psycopg2://test:@localhost:6532/zinc22',
        # 'tin': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5437/tin',
        'tin': 'postgresql+psycopg2://tinuser:usertin@localhost:5434/tin',
        # 'tin2': 'postgresql+psycopg2://tinuser:usertin@localhost:5447/tin'
        '10.20.1.16:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5434/tin',
        '10.20.1.16:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5435/tin',
        '10.20.1.16:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5436/tin',
        '10.20.1.16:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5437/tin',
        '10.20.1.16:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5438/tin',
        '10.20.1.16:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5439/tin',
        '10.20.1.16:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5440/tin',
        '10.20.1.16:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5441/tin',
        '10.20.1.16:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5442/tin',
        '10.20.1.16:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5443/tin',
        '10.20.1.16:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5444/tin',
        '10.20.1.16:5445': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5445/tin',
        '10.20.1.16:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5446/tin',
        '10.20.1.16:5447': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5447/tin',
        '10.20.1.16:5448': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5448/tin',
        '10.20.1.16:5449': 'postgresql+psycopg2://tinuser:usertin@10.20.1.16:5449/tin',
        '10.20.1.17:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5434/tin',
        '10.20.1.17:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5435/tin',
        '10.20.1.17:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5436/tin',
        '10.20.1.17:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5437/tin',
        '10.20.1.17:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5438/tin',
        '10.20.1.17:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5439/tin',
        '10.20.1.17:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5440/tin',
        '10.20.1.17:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5441/tin',
        '10.20.1.17:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5442/tin',
        '10.20.1.17:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5443/tin',
        '10.20.1.17:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5444/tin',
        '10.20.1.17:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.1.17:5446/tin',
        '10.20.1.18:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5434/tin',
        '10.20.1.18:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5435/tin',
        '10.20.1.18:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5436/tin',
        '10.20.1.18:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5437/tin',
        '10.20.1.18:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5438/tin',
        '10.20.1.18:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5439/tin',
        '10.20.1.18:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5440/tin',
        '10.20.1.18:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5441/tin',
        '10.20.1.18:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5442/tin',
        '10.20.1.18:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5443/tin',
        '10.20.1.18:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5444/tin',
        '10.20.1.18:5445': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5445/tin',
        '10.20.1.18:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5446/tin',
        '10.20.1.18:5447': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5447/tin',
        '10.20.1.18:5448': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5448/tin',
        '10.20.1.18:5449': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5449/tin',
        '10.20.1.18:5450': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5450/tin',
        '10.20.1.18:5451': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5451/tin',
        '10.20.1.18:5452': 'postgresql+psycopg2://tinuser:usertin@10.20.1.18:5452/tin',
        '10.20.1.19:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5434/tin',
        '10.20.1.19:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5435/tin',
        '10.20.1.19:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5436/tin',
        '10.20.1.19:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5437/tin',
        '10.20.1.19:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5438/tin',
        '10.20.1.19:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5439/tin',
        '10.20.1.19:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5440/tin',
        '10.20.1.19:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5441/tin',
        '10.20.1.19:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5442/tin',
        '10.20.1.19:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5443/tin',
        '10.20.1.19:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5444/tin',
        '10.20.1.19:5445': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5445/tin',
        '10.20.1.19:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5446/tin',
        '10.20.1.19:5447': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5447/tin',
        '10.20.1.19:5448': 'postgresql+psycopg2://tinuser:usertin@10.20.1.19:5448/tin',
        '10.20.1.20:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5434/tin',
        '10.20.1.20:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5435/tin',
        '10.20.1.20:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5436/tin',
        '10.20.1.20:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5437/tin',
        '10.20.1.20:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5438/tin',
        '10.20.1.20:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5439/tin',
        '10.20.1.20:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5440/tin',
        '10.20.1.20:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5441/tin',
        '10.20.1.20:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5442/tin',
        '10.20.1.20:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5443/tin',
        '10.20.1.20:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5444/tin',
        '10.20.1.20:5445': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5445/tin',
        '10.20.1.20:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5446/tin',
        '10.20.1.20:5447': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5447/tin',
        '10.20.1.20:5448': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5448/tin',
        '10.20.1.20:5449': 'postgresql+psycopg2://tinuser:usertin@10.20.1.20:5449/tin',
        '10.20.5.34:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5434/tin',
        '10.20.5.34:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5435/tin',
        '10.20.5.34:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5436/tin',
        '10.20.5.34:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5437/tin',
        '10.20.5.34:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5438/tin',
        '10.20.5.34:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5439/tin',
        '10.20.5.34:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5440/tin',
        '10.20.5.34:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5441/tin',
        '10.20.5.34:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5442/tin',
        '10.20.5.34:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5443/tin',
        '10.20.5.34:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5444/tin',
        '10.20.5.34:5445': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5445/tin',
        '10.20.5.34:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5446/tin',
        '10.20.5.34:5447': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5447/tin',
        '10.20.5.34:5448': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5448/tin',
        '10.20.5.34:5449': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5449/tin',
        '10.20.5.34:5450': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5450/tin',
        '10.20.5.34:5451': 'postgresql+psycopg2://tinuser:usertin@10.20.5.34:5451/tin',
        '10.20.5.35:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5434/tin',
        '10.20.5.35:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5435/tin',
        '10.20.5.35:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5436/tin',
        '10.20.5.35:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5437/tin',
        '10.20.5.35:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5438/tin',
        '10.20.5.35:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5439/tin',
        '10.20.5.35:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5440/tin',
        '10.20.5.35:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5441/tin',
        '10.20.5.35:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5442/tin',
        '10.20.5.35:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5443/tin',
        '10.20.5.35:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5444/tin',
        '10.20.5.35:5445': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5445/tin',
        '10.20.5.35:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5446/tin',
        '10.20.5.35:5447': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5447/tin',
        '10.20.5.35:5448': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5448/tin',
        '10.20.5.35:5449': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5449/tin',
        '10.20.5.35:5450': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5450/tin',
        '10.20.5.35:5451': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5451/tin',
        '10.20.5.35:5452': 'postgresql+psycopg2://tinuser:usertin@10.20.5.35:5452/tin',
        '10.20.9.19:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5434/tin',
        '10.20.9.19:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5435/tin',
        '10.20.9.19:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5436/tin',
        '10.20.9.19:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5437/tin',
        '10.20.9.19:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5438/tin',
        '10.20.9.19:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5439/tin',
        '10.20.9.19:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5440/tin',
        '10.20.9.19:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5441/tin',
        '10.20.9.19:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5442/tin',
        '10.20.9.19:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5443/tin',
        '10.20.9.19:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.9.19:5444/tin',
        '10.20.9.20:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5434/tin',
        '10.20.9.20:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5435/tin',
        '10.20.9.20:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5436/tin',
        '10.20.9.20:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5437/tin',
        '10.20.9.20:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5438/tin',
        '10.20.9.20:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5439/tin',
        '10.20.9.20:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5440/tin',
        '10.20.9.20:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5441/tin',
        '10.20.9.20:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5442/tin',
        '10.20.9.20:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5443/tin',
        '10.20.9.20:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.9.20:5444/tin',
        '10.20.1.21:5434': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5434/tin',
        '10.20.1.21:5435': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5435/tin',
        '10.20.1.21:5436': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5436/tin',
        '10.20.1.21:5437': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5437/tin',
        '10.20.1.21:5438': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5438/tin',
        '10.20.1.21:5439': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5439/tin',
        '10.20.1.21:5440': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5440/tin',
        '10.20.1.21:5441': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5441/tin',
        '10.20.1.21:5442': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5442/tin',
        '10.20.1.21:5443': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5443/tin',
        '10.20.1.21:5444': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5444/tin',
        '10.20.1.21:5445': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5445/tin',
        '10.20.1.21:5446': 'postgresql+psycopg2://tinuser:usertin@10.20.1.21:5446/tin'
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
    from app.data.models.default_prices import DefaultPrices

    from app.data.models.port_number import PortNumberModel
    from app.data.models.ip_address import IPAddressModel
    from app.data.models.server_mapping import ServerMappingModel
    from app.data.models.tin.substance import SubstanceModel
    from app.data.models.tranche import TrancheModel
    from app.data.models.tin.catalog import CatalogModel, CatalogContentModel, CatalogSubstanceModel, CatalogModel

    from app.data.resources.main import Search, Smiles, SmileList
    from app.data.resources.substance import Substance, Substances, SubstanceList, SubstanceRandomList, SubstanceRandom
    from app.data.resources.catalog_content import CatalogContents, CatalogContent, CatalogContentList
    from app.data.resources.tranche import Tranches

    class MyModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.has_roles('admin')

    admin = Admin(app, name='shoppingcart', template_mode='bootstrap3')
    admin.add_view(MyModelView(Users, db.session))
    admin.add_view(MyModelView(Roles, db.session))
    admin.add_view(MyModelView(Vendors, db.session))
    admin.add_view(MyModelView(AvailableVendors, db.session))
    admin.add_view(MyModelView(DefaultPrices, db.session))

    api.add_resource(Search, '/search.<file_type>')
    api.add_resource(Substance, '/substance')
    api.add_resource(Substances, '/substances.<file_type>')
    sublist_routes = [
        '/sublist',
        '/sublist.<file_type>',
    ]
    api.add_resource(SubstanceList, *sublist_routes)
    api.add_resource(CatalogContent, '/catalog')
    api.add_resource(CatalogContents, '/catalogs.<file_type>')
    api.add_resource(CatalogContentList, '/catlist')
    api.add_resource(Tranches, '/tranches.<file_type>')
    api.add_resource(Smiles, '/smiles.<file_type>')
    smilelist_routes = [
        '/smilelist',
        '/smilelist.<file_type>',
    ]
    api.add_resource(SmileList, *smilelist_routes)
    api.add_resource(SubstanceRandom, '/substance/random.<file_type>')
    api.add_resource(SubstanceRandomList, '/subrandom')


    from app.errors import application as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import application as main_bp
    app.register_blueprint(main_bp)

    db.init_app(app)
    # migrate.init_app(app, db)
    api.init_app(app)
    cors.init_app(app)

    @app.before_request
    def before_request_callback():
        parser = reqparse.RequestParser()
        parser.add_argument('tin_url', type=str)
        args = parser.parse_args()
        tin_url = args.get('tin_url')
        if tin_url:
            db.choose_tenant(tin_url)
        else:
            db.choose_tenant("tin")

    return app
