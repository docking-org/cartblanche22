from flask import Blueprint

application = Blueprint('main', __name__)

from app.main import auth, carts, items, search, vendors, pages, punchout, importData, checkout, configs, \
    order, tranches, default_prices
