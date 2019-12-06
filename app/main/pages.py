from flask import render_template,  url_for
from app.main import application
from flask_login import current_user, login_required

@application.route('/', methods=['GET'])
@application.route('/cartblanche', methods=['GET'])
@login_required
def cartblanche():
    return render_template('cartblanche.html')