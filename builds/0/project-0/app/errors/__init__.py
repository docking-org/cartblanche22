from flask import Blueprint

application = Blueprint('errors', __name__)

from app.errors import handlers
