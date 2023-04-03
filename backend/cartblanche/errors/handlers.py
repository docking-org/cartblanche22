from flask import render_template
from cartblanche.app import db
from cartblanche.errors import application


@app.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
