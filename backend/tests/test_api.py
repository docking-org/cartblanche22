from urllib.parse import urlencode
import json

def call(flask_app_client, path, params):
    url = path
    data = params
    response = flask_app_client.get(url, data=data)
    return json.loads(response.data.decode('utf-8'))

def test_sub_id_search(flask_app_client):
    response = call(flask_app_client, '/substances.json', {'zinc_ids': 'ZINCar0000000p57'})[0]
    check_result(response)

def test_smiles_search(flask_app_client):
    response = call(flask_app_client, '/smiles.json', {'smiles': 'CCN(C(=O)COc1ccccc1)c1ccccc1', 'dist': '0', 'adist': '0'})[0]
    check_result(response)
    
    # response = call(flask_app_client, '/smiles.json', {'smiles': 'CCN(C(=O)COc1ccccc1)c1ccccc1', 'dist': '0', 'adist': '0', "database":'zinc20,zinc22'})[0]
    
    check_result(response)
    
def test_supplier_search(flask_app_client):
    response = call(flask_app_client, '/catitems.json', {'supplier_codes': 's_22__9598818__14482412'})[0]
    check_result(response)

def check_result(response):
    assert response.get('catalogs') != None
    assert response.get('smiles') != None
    assert response.get('sub_id') != None
    assert response.get('tranche') != None
    assert response.get('tranche_details') != None
    assert response.get('zinc_id') != None

