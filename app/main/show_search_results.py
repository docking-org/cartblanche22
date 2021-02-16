from flask import render_template, request, json, Response
from app.main import application

base_url = "http://cartblanche22.docking.org/"
swp_server = 'http://swp.docking.org'
sw_server = 'http://swp.docking.org'


@application.route('/downloadSearchResult', methods=["GET"])
def downloadSearchResult():
    data = request.args['data']
    # data = session['search_result']
    download_filename = 'searchResult.txt'
    response = Response(json.dumps(data), mimetype='text/plain')
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
    return response


@application.route('/showSmilesResult/', methods=["GET"])
def showSmilesResult():
    data = request.args['data']
    print(data)
    return render_template('search/search_result_smile.html', data_=json.loads(data))


@application.route('/showSupplierResult/', methods=["GET"])
def showSupplierResult():
    data = request.args['data']
    print('showSupplierResult', data)
    return render_template('search/search_result.html', data_=json.loads(data))


@application.route('/showZincListResult/', methods=["GET"])
def showZincListResult():
    data = request.args['data']
    print('showZincListResult', data)
    return render_template('search/search_result.html', data_=json.loads(data))
