from flask import jsonify, render_template, request
from flask_login import current_user
from app.main import application
from app import db
import argparse, time
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import os

@application.route('/gsheet', methods=["POST"])
def gsheet():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "credentials.json")
    
    print('cart data in gsheet')
    SCOPES = "https://www.googleapis.com/auth/spreadsheets"
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        flow = client.flow_from_clientsecrets(json_url, SCOPES)
        creds = tools.run_flow(flow, store, flags)
    SHEETS = discovery.build('sheets', 'v4', http=creds.authorize(Http()))
    data = {'properties': {'title': 'Cart data [%s]' % time.ctime()}}
    res = SHEETS.spreadsheets().create(body=data).execute()
    SHEET_ID = res['spreadsheetId']
    print('Created "%s"' % res['properties']['title'])
    print(res)
    values = [['No', 'identifier', 'db', 'catalog name', 'supplier_code', 'pack size', 'unit', 'price', 'shipping',
            'purchase qty ', 'total']]
    data = request.get_json()
    for i in data:
        row = [i['num'], i['identifier'], i['db'], i['cat_name'], i['supplier_code'], i['quantity'], i['unit'], i['price'],
            i['shipping'], i['purchase'], i['total']]
        values.append(row)


    body = {
        'values': values
    }
    SHEETS.spreadsheets().values().update(
        spreadsheetId=SHEET_ID, range='A1', valueInputOption='RAW', body=body).execute()
    return jsonify(res['spreadsheetUrl'])