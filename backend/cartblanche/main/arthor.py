import os
import requests
from cartblanche.app import app
from flask import render_template, request


@app.route('/arthor')
def arthor():
    return render_template('search/arthor.html', arthor_url="https://arthor.docking.org")


@app.route('/arthorp')
def arthorp():
    return render_template('search/arthor.html', arthor_url="https://arthorp.docking.org")

@app.route('/arthor/get_maps')
def get_maps():
    server = request.args.get('server')
    if server == 'arthorp':
        url = os.getenv('ARTHOR_PRIVATE_URL')
    else:
        url = os.getenv('ARTHOR_PUBLIC_URL')

    if not url:
        env_var = 'ARTHOR_PRIVATE_URL' if server == 'arthorp' else 'ARTHOR_PUBLIC_URL'
        return {'error': f'{env_var} is not configured'}, 500

    raw = requests.get(f"{url}/dt/data").json()
    return raw
    
    

    

