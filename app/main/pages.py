from flask import render_template,  url_for
from app.main import application
from flask_login import current_user, login_required

@application.route('/', methods=['GET'])
@application.route('/cartblanche', methods=['GET'])
def cartblanche():
    return render_template('cartblanche.html')

@application.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')