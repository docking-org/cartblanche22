from cartblanche.app import app 
from flask import render_template, request, jsonify, url_for
import requests
import json 
sw_server = 'https://sw.docking.org'
swp_server = 'https://swp.docking.org'
swc_server = 'https://swc.docking.org'

@app.route('/sw')
def sw():
    try:
        config = requests.get(sw_server + '/search/config').json()
    except:
        return render_template('errors/500.html')
    try:
        maps = requests.get(sw_server + '/search/maps').json()
    except:
        return render_template('errors/500.html')
    smiles = request.args.get('smiles')
    print(smiles)
    return render_template('search/sw.html', config=json.dumps(config), maps=json.dumps(maps), sw_server=sw_server, withCredentials=False)


@app.route('/swp')
def swp():
    try:
        config = requests.get(swp_server + '/search/config',
                              auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/403.html')
    try:
        maps = requests.get(swp_server + '/search/maps',
                            auth=('gpcr', 'xtal')).json()
    except:
        return render_template('errors/403.html')
    return render_template('search/sw.html', config=json.dumps(config), maps=json.dumps(maps), sw_server=swp_server, withCredentials=True)


@app.route('/swc')
def swc():
    try:
        config = requests.get(swc_server + '/search/config',
                              auth=('big', 'fat secret')).json()
    except:
        return render_template('errors/403.html')
    try:
        maps = requests.get(swc_server + '/search/maps',
                            auth=('big', 'fat secret')).json()
    except:
        return render_template('errors/403.html')
    return render_template('search/sw.html', config=json.dumps(config), maps=json.dumps(maps), sw_server=swc_server, withCredentials=True)