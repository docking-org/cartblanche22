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
        
    def apply_pool_defaults(self, app, options):
        super().apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True

db = MultiTenantSQLAlchemy()
migrate = Migrate(compare_type=True)
login = LoginManager()
bootstrap = Bootstrap()
mail = Mail()
api = Api()
cors = CORS()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #TIN URLS MOVED TO CONFIG!
    
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

    from app.data.tasks.search_zinc import SearchJobSubstance, SearchJobSupplier
    from app.data.tasks.search_smiles import SearchSmiles

    class MyModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.has_roles('admin')

    admin = Admin(app, name='shoppingcart', template_mode='bootstrap3')
    admin.add_view(MyModelView(Users, db.session))
    admin.add_view(MyModelView(Roles, db.session))
    # admin.add_view(MyModelView(Vendors, db.session))
    # admin.add_view(MyModelView(AvailableVendors, db.session))
    admin.add_view(MyModelView(DefaultPrices, db.session))

    api.add_resource(Search, '/search.<file_type>')
    api.add_resource(SearchJobSubstance, '/searchJobSubstance')
    api.add_resource(SearchJobSupplier, '/searchJobSupplier')
    api.add_resource(SearchSmiles, '/searchSmiles')
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
    api.init_app(app)
    cors.init_app(app)
    # migrate.init_app(app, db)
    
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

