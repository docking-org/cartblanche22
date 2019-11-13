from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()


def create_app(config_class=Config):
    application = app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login.init_app(app)
    login.login_view = 'main.login'

    bootstrap.init_app(app)

    from app.errors import application as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import application as main_bp
    app.register_blueprint(main_bp)

    return app

# from app import models
