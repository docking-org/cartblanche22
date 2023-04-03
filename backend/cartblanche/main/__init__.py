from flask import Blueprint

application = Blueprint('main', __name__)

from cartblanche.main import auth, items, vendors, pages, punchout, importData, checkout, configs, \
    order, tranches, default_prices, arthor, sw, carts
