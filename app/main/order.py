from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user
from app.main import application
from app.data.models.users import Users
from app import db
from app.email import prepare_email_chemspace
import tablib


@application.route('/order_chemspace', methods=['GET', 'POST'])
def order_chemspace():
    data = request.get_json()
    print(data)
    headers = ('No', 'identifier', 'db', 'catalog name', 'supplier_code', 'pack size', 'unit', 'price', 'shipping',
               'purchase qty ', 'total', 'Require exact stereochemistry?', 'Quote close analogs?')
    data_ = tablib.Dataset(headers=headers)
    for i in data:
        row = (i['num'], i['identifier'], i['db'], i['cat_name'], i['supplier_code'], i['quantity'], i['unit'],
               i['price'], i['shipping'], i['purchase'], i['total'], i['stereochemistry'], i['analogs'])
        data_.append(row)
    file = data_.export('xls')
    body = 'Have a nice day!'
    prepare_email_chemspace(current_user, body, file)
    return jsonify('success')
