from flask import Blueprint

application = Blueprint('main', __name__)

from app.main import routes
