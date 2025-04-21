from flask import Flask, g, current_app, request, send_from_directory
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


from flask_bootstrap import Bootstrap

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
    #allow cache for a month for application/wasm files
    
    if request.path.endswith('.wasm') or request.path.endswith("RDKit_minimal.js"):
        # r.cache_control.max_age = 2592000
        # r.cache_control.public = True
        r.headers["Cache-Control"] = "public, max-age=2592000"
    if request.path.endswith(".css"):
        #one day
        r.headers["Cache-Control"] = "public, max-age=86400"
    
    #set content type for js, wasm, css files
    if request.path.endswith('.wasm'):
        r.headers["Content-Type"] = "application/wasm"
    if request.path.endswith('.js'):
        r.headers["Content-Type"] = "application/javascript"
    if request.path.endswith('.css'):
        r.headers["Content-Type"] = "text/css"
    if request.path.endswith('.json'):
        r.headers["Content-Type"] = "application/json"  
        
        
    return r
    
def create_app(config_class=Config):
    app.config.from_object(Config)
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)


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
