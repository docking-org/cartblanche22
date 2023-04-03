from flask import Flask, g, current_app, request, send_from_directory
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
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login = LoginManager()
bootstrap = Bootstrap()
mail = Mail()
api = Api()
cors = CORS()
jwt = JWTManager()
app = Flask(__name__, static_folder = "../../build")
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    
    return r
    
def create_app(config_class=Config):
    app.config.from_object(Config)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
    
   
    login.init_app(app)
    login.login_view = 'main.login'

    mail.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    
    api.init_app(app)
    cors.init_app(app)


    from cartblanche.main import application as main_bp
    app.register_blueprint(main_bp)

    from cartblanche.main.search import search_bp
    app.register_blueprint(search_bp)



    return app
