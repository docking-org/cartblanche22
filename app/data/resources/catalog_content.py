from flask_restful import Resource, reqparse
from app.data.models.tin.catalog import CatalogContentModel
from app.data.models.server_mapping import ServerMappingModel
from werkzeug.datastructures import FileStorage
from flask import jsonify, current_app, request
import requests
from collections import defaultdict
import grequests
import json

parser = reqparse.RequestParser()


class CatalogContentList(Resource):
    def post(self, file_type=None):
        parser.add_argument('supplier_code-in', type=str)
        args = parser.parse_args()
        supplier_codes = args.get('supplier_code-in').split(',')
        args['supplier_code-in'] = supplier_codes
        return self.getList(args, file_type)

    @classmethod
    def getList(cls, args, file_type=None):
        supplier_codes = args.get('supplier_code-in')

        tin_urls = {}
        tin_list = []
        server_mappings = ServerMappingModel.query.distinct(
            ServerMappingModel.ip_fk,
            ServerMappingModel.port_fk).limit(2).all()

        for sm in server_mappings:
            if sm.tranches:
                url = "{}:{}".format(sm.ip_address.ip, sm.port_number.port)
                tin_list.append(url)
                tin_urls[url] = "ZINC{}{}".format(sm.tranches[0].mwt, sm.tranches[0].logp)

        s_codes = ','.join(supplier_codes)
        url = 'http://{}/catalog'.format(request.host)
        resp = (grequests.post(url, data={'supplier_codes': s_codes, 'tin_url': k}) for k, v in tin_urls.items())

        data = defaultdict(list)
        data['items'].extend([json.loads(res.text) for res in grequests.map(resp) if 'Not found' not in res.text])

        if not data['items']:
            return {'message': 'Not found'}, 404

        data['items'] = data['items'][0]
        return jsonify(data)


class CatalogContent(Resource):
    def post(self):
        parser.add_argument('supplier_codes', type=str)
        parser.add_argument('tin_url', type=str)
        args = parser.parse_args()
        lines = args.get('supplier_codes').split(',')
        catContents =  CatalogContentModel.query.filter(CatalogContentModel.supplier_code.in_(lines)).all()
        data = []
        for cc in catContents:
            data.extend([sub.json() for sub in cc.substances])

        if data:
            return jsonify(data)
        return {'message': 'Not found'}, 404


    # def get(self, tin_url, lines):
    #     current_app.config['TIN_URL'] = tin_url
    #     catContents =  CatalogContentModel.query.filter(CatalogContentModel.supplier_code.in_(lines)).all()
    #     for cc in catContents:
    #         data['items'].extend([sub.json(v) for sub in cc.substances])
    #     return jsonify(data)


class CatalogContents(Resource): 
    def post(self, file_type=None):
        parser.add_argument('supplier_code-in', location='files', type=FileStorage, required=True)
        args = parser.parse_args()
        uploaded_file = args.get('supplier_code-in').stream.read().decode("latin-1")
        lines = [x for x in uploaded_file.split('\n') if x]
        args['supplier_code-in'] = lines

        return CatalogContentList.getList(args, file_type)

