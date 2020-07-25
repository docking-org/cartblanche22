from flask import jsonify, render_template, request, url_for
from flask_login import current_user
from app.main import application
from app.main.google import Create_Service
from app import db
import argparse, time
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import os
import gspread
import os
import asyncio


def main(data):
    print(data)


@application.route('/gsheet', methods=["POST"])
def gsheet():
    data = request.get_json()
    FOLDER_PATH = os.path.realpath(os.path.dirname(__file__))
    CLIENT_SECRET_FILE = os.path.join(FOLDER_PATH, 'credentials.json')
    API_SERVICE_NAME = 'sheets'
    API_VERSION = 'v4'
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    service = Create_Service(CLIENT_SECRET_FILE, API_SERVICE_NAME, API_VERSION, SCOPES)
    if service is None:
        return jsonify(url_for('main.directCheckout')), 400
        # return "authentication failed"
    header = {'properties': {'title': 'Cart data [%s]' % time.ctime()}}
    res = service.spreadsheets().create(body=header).execute()
    SHEET_ID = res['spreadsheetId']
    print('Created "%s"' % res['properties']['title'])
    print(res)
    values = [['No', 'identifier', 'db', 'catalog name', 'supplier_code', 'pack size', 'unit', 'price', 'shipping',
               'purchase qty ', 'total']]

    for i in data:
        row = [i['num'], i['identifier'], i['db'], i['cat_name'], i['supplier_code'], i['quantity'], i['unit'],
               i['price'],
               i['shipping'], i['purchase'], i['total']]
        values.append(row)

    body = {
        'values': values
    }
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID, range='A1', valueInputOption='RAW', body=body).execute()
    return jsonify(res['spreadsheetUrl']), 200


@application.route('/gsheetOld', methods=["POST"])
def gsheetOld():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "credentials.json")

    print('cart data in gsheet')
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive",
              "https://www.googleapis.com/auth/drive.file"]
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
    drive = discovery.build('drive', 'v3', credentials=creds)
    domain_permission = {
        'type': 'domain',
        'role': 'writer',
        'emailAddress': 'munkhzulk@gmail.com',
        # Magic almost undocumented variable which makes files appear in your Google Drive
        'allowFileDiscovery': True,
    }

    req = drive.permissions().create(fileId=SHEET_ID, body=domain_permission, fields="id")
    req.execute()
    return jsonify(res['spreadsheetUrl'])
