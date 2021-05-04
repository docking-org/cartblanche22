from flask_restful import Resource, reqparse
from app.data.models.tin.catalog import CatalogContentModel
from app.data.models.server_mapping import ServerMappingModel
from werkzeug.datastructures import FileStorage
from app.helpers.representations import OBJECT_MIMETYPE_TO_FORMATTER
from flask import jsonify, current_app, request, make_response
from collections import defaultdict
import grequests
import json
import time
from sqlalchemy import func
from flask_csv import send_csv
from datetime import datetime
import itertools

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
            ServerMappingModel.port_fk).all()

        for sm in server_mappings:
            if sm.tranches:
                url = "{}:{}".format(sm.ip_address.ip, sm.port_number.port)
                tin_list.append(url)
                tin_urls[url] = "ZINC{}{}".format(sm.tranches[0].mwt, sm.tranches[0].logp)

        s_codes = ','.join(supplier_codes)
        url = 'https://{}/catalog'.format(request.host)
        resp = (grequests.post(url, data={'supplier_codes': s_codes, 'tin_url': k, 'zinc_id_start': v}, timeout=15) for
                k, v in tin_urls.items())

        results = [json.loads(res.text) for res in grequests.map(resp) if res and 'Not found' not in res.text]
        flat_list = itertools.chain.from_iterable(results)
        data = defaultdict(list)
        data['items'] = list(flat_list)

        if not data['items']:
            return {'message': 'Not found'}, 404

        str_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        if file_type == 'csv':
            keys = list(data['items'][0].keys())
            return send_csv(data['items'], "supplier_code_{}.csv".format(str_time), keys)
        elif file_type == 'txt':
            Formatter = OBJECT_MIMETYPE_TO_FORMATTER["text/plain"]
            keys = list(data['items'][0].keys())
            formatter = Formatter(fields=keys)
            ret_list = ""
            for line in formatter(data['items']):
                ret_list += line

            download_filename = "search_{}.txt".format(str_time)
            response = make_response(ret_list, 200)
            response.mimetype = "text/plain"
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
            return response
        else:
            return jsonify(data)


class CatalogContent(Resource):
    def post(self):
        parser.add_argument('supplier_codes', type=str)
        parser.add_argument('tin_url', type=str)
        parser.add_argument('zinc_id_start', type=str)
        args = parser.parse_args()
        lines = args.get('supplier_codes').lower().split(',')
        try:
            time1 = time.time()
            catContents = CatalogContentModel.query.filter(
                func.lower(CatalogContentModel.supplier_code).in_(lines)).all()

            time2 = time.time()
            strtime1 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time1))
            strtime2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time2))
            print('{:s} !!!!!!!!!! started at {} and finished at {}. It took {:.3f} s'.format(args.get('tin_url'),
                                                                                              strtime1, strtime2,
                                                                                              (time2 - time1) % 60))

            data = []
            for cc in catContents:
                data.extend([sub.json2(args.get('zinc_id_start')) for sub in cc.substances])

            if data:
                return jsonify(data)

        except Exception as e:
            print("Exception!!!!!!!!!!: ", args.get('tin_url'), " error:", e)
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
