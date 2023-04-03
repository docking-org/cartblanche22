from flask import Blueprint

application = Blueprint('errors', __name__)

from cartblanche.errors import handlers
