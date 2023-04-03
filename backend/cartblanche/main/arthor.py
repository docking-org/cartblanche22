from cartblanche.app import app 
from flask import render_template

@app.route('/arthor')
def arthor():
    return render_template('search/arthor.html', arthor_url="https://arthor.docking.org")


@app.route('/arthorp')
def arthorp():
    return render_template('search/arthor.html', arthor_url="https://arthorp.docking.org")

