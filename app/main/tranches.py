from flask import render_template
from app.main import application

@application.route('/tranches', methods=['GET'])
def tranches():
    return render_template('tranches/home.html')