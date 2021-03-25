from flask import render_template, request, json, Response
from app.main import application
import requests
base_url = "https://cartblanche22.docking.org/"
swp_server = 'https://swp.docking.org'
sw_server = 'https://sw.docking.org'


@application.route('/downloadZincListResult', methods=["GET"])
def downloadZincListResult():
    value = request.args['value']
    print('from downloadSearchResult')
    print(value)
    files = {
        'zinc_id-in': value
    }
    response = requests.post(base_url + 'sublist', params=files)
    if response:
        data = response.json()
        download_filename = 'searchResult_zincids.txt'
        response = Response(json.dumps(data), mimetype='text/plain')
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
        return response
    else:
        print(response)
        return render_template('errors/404.html', lines=value), 404


@application.route('/downloadSupplierResult', methods=["GET"])
def downloadSupplierResult():
    value = request.args['value']
    print('from downloadSupplierResult')
    print(value)
    files = {
        'supplier_code-in': value
    }
    response = requests.post(base_url + 'catlist', params=files)
    if response:
        data = response.json()
        download_filename = 'searchResult_suppliercodes.txt'
        response = Response(json.dumps(data), mimetype='text/plain')
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
        return response
    else:
        print(response)
        return render_template('errors/404.html', lines=value), 404


@application.route('/downloadSmilesResult', methods=["GET"])
def downloadSmilesResult():
    value = request.args['value']
    dist = request.args['dist']
    print('from downloadSmilesResult')
    print(value)
    files = {
        'smiles-in': value,
        'dist': dist,
    }
    response = requests.post(base_url + 'smilelist', params=files)
    if response:
        data = response.json()
        download_filename = 'searchResult_smiles.txt'
        response = Response(json.dumps(data), mimetype='text/plain')
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
        return response
    else:
        print(response)
        return render_template('errors/404.html', lines=value), 404


@application.route('/showSmilesResult/', methods=["GET"])
def showSmilesResult():
    value = request.args['value']
    dist = request.args['dist']
    adist = request.args['adist']
    print('from downloadSmilesResult')
    print(value)
    files = {
        'smiles-in': value,
        'dist': dist,
        'adist': adist,
    }
    try:
        response = requests.post(base_url + 'smilelist', params=files, timeout=120)
        data = response.json()
        print(data)
        return render_template('search/search_result_smile.html', data_=data, value=value, dist=dist)
    except requests.exceptions.Timeout as e:
        print(e)
        return render_template('errors/search404.html', header="We can't find your search. Our server responds too slow", lines=value), 404
    except:
        return render_template('errors/search404.html', header='We found 0 matches', lines=value), 404


@application.route('/showSupplierResult/', methods=["GET"])
def showSupplierResult():
    value = request.args['value']
    print('from showSupplierResult')
    print(value)
    files = {
        'supplier_code-in': value
    }
    try:
        response = requests.post(base_url + 'catlist', params=files, timeout=120)
        data = response.json()
        print(data)
        return render_template('search/search_result.html', data_=data['items'], value=value, search='supplier')
    except requests.exceptions.Timeout as e:
        print(e)
        return render_template('errors/search404.html', header="We can't find your search. Our server responds too slow", lines=value), 404
    except:
        return render_template('errors/search404.html', header='We found 0 matches', lines=value), 404

@application.route('/showZincListResult/', methods=["GET"])
def showZincListResult():
    value = request.args['value']
    print('showZincListResult')
    print(value)
    files = {
        'zinc_id-in': value
    }
    try:
        response = requests.post(base_url + 'sublist', params=files, timeout=120)
        data = response.json()
        print(data)
        return render_template('search/search_result.html', data_=data['items'], value=value, search='zinc')
    except requests.exceptions.Timeout as e:
        print(e)
        return render_template('errors/search404.html', header="We can't find your search. Our server responds too slow", lines=value), 404
    except:
        return render_template('errors/search404.html', header='We found 0 matches', lines=value), 404
