from flask import redirect, jsonify, request, url_for, session, render_template
from app.main import application
from app.data.models.default_prices import DefaultPrices


@application.route("/getDefaultPrices", methods= ['GET'])
def getDefaultPrices():
     prices = DefaultPrices.query.all()
     print(prices)