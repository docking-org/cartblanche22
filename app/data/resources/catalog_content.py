from flask_restful import Resource, reqparse
from app.data.models.tin.catalog import CatalogContentModel
from app.data.models.server_mapping import ServerMappingModel
from werkzeug.datastructures import FileStorage
from app.helpers.representations import OBJECT_MIMETYPE_TO_FORMATTER
from app.helpers.validation import get_all_unique_tin_servers
from flask import jsonify, current_app, request, make_response
from collections import defaultdict
import grequests
import json
import time
from sqlalchemy import func, and_
from flask_csv import send_csv
from datetime import datetime
import itertools
from app.email_send import send_search_log

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

        tin_urls = get_all_unique_tin_servers()
        # tin_list = []
        # server_mappings = ServerMappingModel.query.distinct(
        #     ServerMappingModel.ip_fk,
        #     ServerMappingModel.port_fk).all()
        #
        # for sm in server_mappings:
        #     if sm.tranches:
        #         url = "{}:{}".format(sm.ip_address.ip, sm.port_number.port)
        #         # tin_list.append(url)
        #         tin_urls[url] = "ZINC{}{}".format(sm.tranches[0].mwt, sm.tranches[0].logp)
        s_codes = ','.join(supplier_codes)
        expected_result_count = len(supplier_codes)
        url = 'https://{}/catalog'.format(request.host)
        time1 = time.time()
        resp = (grequests.post(url, data={'supplier_codes': s_codes, 'tin_url': t}, timeout=15) for t in tin_urls)

        results = [json.loads(res.text) for res in grequests.map(resp) if res and 'Not found' not in res.text]

        flat_list = itertools.chain.from_iterable(results)
        data = defaultdict(list)
        data['items'] = list(flat_list)

        data['search_info'] = [d['search_info'] for d in data['items'] if 'search_info' in d]
        # gets only results from flat list
        data['items'] = [d for d in data['items'] if 'search_info' not in d]

        if len(data['items']) < expected_result_count:
            search_info = {
                'tin_url': 'all tin urls',
                'error': "expected result count was {}. But only returned {}".format(expected_result_count, len(data['items'])),
                'elapsed_time': 'Whole search from all TIN servers took {:.3f} s'.format((time.time() - time1) % 60)
            }
            data['search_info'].append(search_info)
            send_search_log(data['search_info'])

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
        args = parser.parse_args()
        lines = args.get('supplier_codes').split(',')
        tin_url = args.get('tin_url')
        time1 = time.time()
        print("tin_url=========================", tin_url)
        strtime1 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time1))
        try:
            catContents = CatalogContentModel.query.filter(
                and_(CatalogContentModel.supplier_code.in_(lines), CatalogContentModel.depleted == False)).all()
        except Exception as e:
            search_info = {
                'tin_url': args.get('tin_url'),
                'error': 'SQL SERVER CONNECTION ERROR',
                'elapsed_time': 'It took {:.3f} s'.format((time.time() - time1) % 60)
            }
            return jsonify([{'search_info': search_info}])

        time2 = time.time()
        strtime2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time2))
        elapsed_time = '{:s} !!!!!!!!!! started at {} and finished at {}. It took {:.3f} s'.format(tin_url,
                                                                                          strtime1, strtime2,
                                                                                          (time2 - time1) % 60)
        search_info = {
            'tin_url': args.get('tin_url'),
            'error': 'No error on this server. Returned {} result(s) from this server'.format(len(catContents)),
            'elapsed_time': elapsed_time
        }
        return jsonify([{'search_info': search_info}])

        data = []
        for cc in catContents:
            data.extend([sub.json2() for sub in cc.substances])

        if data:
            data.append({'search_info': search_info})
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
        parser.add_argument('supplier_code-in', location='files', type=FileStorage)
        args = parser.parse_args()
        uploaded_file = args.get('supplier_code-in').stream.read().decode("latin-1")
        lines = [x for x in uploaded_file.split('\n') if x]
        args['supplier_code-in'] = lines

        return CatalogContentList.getList(args, file_type)
