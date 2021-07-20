from flask_restful import Resource, reqparse
from app.data.models.tin.substance import SubstanceModel
from app.data.models.tranche import TrancheModel
from werkzeug.datastructures import FileStorage
from app.helpers.validation import base10, get_all_tin_url, get_all_unique_tin_servers
from app.helpers.representations import OBJECT_MIMETYPE_TO_FORMATTER
from app import db
from flask import jsonify, current_app, request, make_response
from collections import defaultdict
import grequests
import json
import time
from flask_csv import send_csv
from datetime import datetime
import itertools
import logging
import requests
import random
import re
from app.email_send import sendSearchLog

# from app.formatters import (
#     CsvFormatter,
#     IteratedOutput,
#     JsonFormatter,
#     JsonStreamFormatter,
#     TxtFormatter,
#     XmlFormatter,
# )


logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()

parser = reqparse.RequestParser()

mimetypes = {
    'csv': 'text/csv',
    'txt': 'text/plain',
    'json': 'application/javascript',
    'jsons': 'application/javascript;stream',
    'xml': 'application/xml',
}


# formatters = {
#     'text/csv': IteratedOutput.construct_wrapped(CsvFormatter),
#     'application/javascript': IteratedOutput.construct_wrapped(JsonFormatter),
#     'application/javascript;stream': IteratedOutput.construct_wrapped(JsonStreamFormatter),
#     'application/xml': IteratedOutput.construct_wrapped(XmlFormatter),
#     'text/plain': IteratedOutput.construct_wrapped(TxtFormatter),
# }

class SubstanceList(Resource):
    def post(self, file_type=None):
        parser.add_argument('zinc_id-in', type=str)
        parser.add_argument('output_fields', type=str)
        args = parser.parse_args()
        zinc_ids = args.get('zinc_id-in').split(',')
        args['zinc_id-in'] = zinc_ids
        return self.getList(args, file_type)

    @classmethod
    def getList(cls, args, file_type=None):
        zinc_ids = sorted(args.get('zinc_id-in'))
        output_fields = ""
        if args.get('output_fields'):
            output_fields = args.get('output_fields')
        show_missing = ""
        if args.get('show_missing'):
            show_missing = args.get('show_missing')
        dict_ids = defaultdict(list)
        dict_zinc_ids = defaultdict(list)
        dict_subid_zinc_id = defaultdict(list)

        overlimit_count = 0
        chunk = 1000
        if args.get('chunk'):
            chunk = args.get('chunk')
        timeout = 15
        if args.get('timeout'):
            timeout = args.get('timeout')

        urls = get_all_tin_url()
        # print('tin  urls:', urls)

        for zinc_id in zinc_ids:
            if zinc_id:
                url = urls.get(zinc_id[4:6])
                # pattern = "^ZINC[a-zA-Z]{2}[0-9a-zA-Z]+"
                pattern = "^ZINC[1-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z]+"
                if not url or not re.match(pattern, zinc_id):
                    print("url or zinc_id not found", zinc_id)
                    continue
                    # return {'message': 'No server is mapped to {}. Please contact with Irwin Lab.'.format(zinc_id)}, 404

                if len(dict_ids[url]) > chunk:
                    dict_ids["{}-{}".format(url, overlimit_count)] = dict_ids[url]
                    dict_ids[url] = [base10(zinc_id)]
                    dict_zinc_ids[url] = [zinc_id]
                    overlimit_count += 1
                else:
                    dict_ids[url].append(base10(zinc_id))
                    dict_zinc_ids[url].append(zinc_id)
                dict_subid_zinc_id[int(base10(zinc_id))].append(zinc_id)

        url = 'https://{}/substance'.format(request.host)

        for k, v in dict_ids.items():
            print("TIN URLS ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print(k, len(v))
            # print('sub_ids', ','.join([str(i) for i in v]))
            # print( 'tin_url', k.split('-')[0])
            # print(k, v)
        # print("len(dict_ids)", len(dict_ids))
        # print(url)
        # print("before response")
        resp = (grequests.post(url,
                               data={
                                   'sub_ids': ','.join([str(i) for i in v]),
                                   'zinc_ids': ','.join([str(i) for i in dict_zinc_ids[k]]),
                                   'tin_url': k.split('-')[0],
                                   'output_fields': output_fields,
                                   'show_missing': show_missing
                               }, timeout=timeout) for k, v in dict_ids.items())
        # print("after response")
        data = defaultdict(list)
        results = []
        error = []
        for res in grequests.map(resp):
            print('printing grequests.map', res)
            if res and 'Not found' not in res.text:
                results.append(json.loads(res.text))
            if not res == None and res.status_code == 404:
                error.append(json.loads(res.text))



        # results = [json.loads(res.text) for res in grequests.map(resp) if res and 'Not found' not in res.text]

        print('results', results)
        print('error', error)
        if len(error) > 0:
            sendSearchLog(error)
        if show_missing.lower() == 'on':

            def get_zinc_ids(vals):
                return ["{} {}".format(dict_subid_zinc_id.get(int(v))[0], v) for v in vals]

            res = [{k: get_zinc_ids(vals) for k, vals in res.items()} for res in results]
            print('returning res', res)
            return res

        flat_list = itertools.chain.from_iterable(results)

        data['items'] = list(flat_list)
        print( data['items'])
        print("received count. data['items']:", len(data['items']))

        if not data['items']:
            print('return 404')
            return {'message': 'Not found'}, 404

        str_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        if file_type == 'csv':
            keys = list(data['items'][0].keys())
            return send_csv(data['items'], "zinc_id_search_{}.csv".format(str_time), keys)
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


class Substance(Resource):
    def post(self, file_type=None):
        parser.add_argument('sub_ids', type=str)
        parser.add_argument('tin_url', type=str)
        parser.add_argument('output_fields', type=str)
        parser.add_argument('show_missing', type=str)
        # args = parser.parse_args()
        # sub_id_list = args.get('sub_ids').split(',')
        # sub_ids = (int(id) for id in sub_id_list)
        # sub_ids_len = len(args.get('sub_ids').split(','))
        sub_id_list = request.values.get('sub_ids').split(',')
        zinc_id_list = set(request.values.get('zinc_ids').split(','))
        sub_ids = (int(id) for id in sub_id_list)
        sub_ids_len = len(sub_id_list)
        args = request.values
        print("REQUESTED TIN_URL from Substance POST", request.values.get('tin_url'))
        time1 = time.time()
        substances = SubstanceModel.query.filter(SubstanceModel.sub_id.in_(sub_ids)).all()
        # substances = db.session.query(SubstanceModel).filter(SubstanceModel.sub_id.in_(sub_ids)).all()

        time2 = time.time()
        strtime1 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time1))
        strtime2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time2))
        print('{:s} !!!!!!!!!! started at {} and finished at {}. It took {:.3f} s'.format(args.get('tin_url'), strtime1,
                                                                                          strtime2,
                                                                                          (time2 - time1) % 60))
        print("{} server returned {} results and {} result was expecting".format(args.get('tin_url'), len(substances),
                                                                                 sub_ids_len))

        # if len(substances) != sub_ids_len:
        #     logger.info(args.get('sub_ids'))
        print('substances', substances)
        if substances is None or len(substances) == 0:
            print('return 404 because None')
            return {'message': 'Substance not found with sub_id(s): {}'.format(sub_id_list),
                    'tin_url': args.get('tin_url'),
                    'returned': len(substances),
                    'expecting': sub_ids_len,
                    'time': (time2 - time1) % 60
                    }, 404

        data = []
        for sub in substances:
            data_dict = sub.json()
            sub_id_list.remove(str(data_dict['sub_id']))

            if 'output_fields' in args and args.get('output_fields'):

                output_fields = args.get('output_fields').replace(" ", "").split(",")
                output_fields = [i for i in data_dict.keys() if i in output_fields]

                new_dict = {output_field: data_dict[output_field] for output_field in output_fields}
                data_dict = new_dict
            if data_dict['zinc_id'] in zinc_id_list:
                data.append(data_dict)

        if args.get('show_missing') and args.get('show_missing').lower() == 'on':
            print("missing sub_ids:", sub_id_list)
            return jsonify({args.get('tin_url'): sub_id_list})

        if data:
            return jsonify(data)
        return {'message': 'Not found',
                'tin_url' : args.get('tin_url'),
                'returned' : len(substances),
                'expecting': sub_ids_len,
                'time' : (time2 - time1) % 60
                }, 404


class Substances(Resource):
    def post(self, file_type=None):
        parser.add_argument('zinc_id-in', location='files', type=FileStorage, required=True)
        parser.add_argument('chunk', type=int)
        parser.add_argument('timeout', type=int)
        parser.add_argument('output_fields', type=str)
        parser.add_argument('show_missing', type=str)
        args = parser.parse_args()

        uploaded_file = args.get('zinc_id-in').stream.read().decode("latin-1")

        lines = uploaded_file.split('\n')
        args['zinc_id-in'] = lines
        return SubstanceList.getList(args, file_type)


class SubstanceRandomList(Resource):
    def post(self, file_type=None):
        parser.add_argument('random', type=str)
        parser.add_argument('tin_url', type=str)
        parser.add_argument('output_fields', type=str)
        args = parser.parse_args()
        random = args.get('random')

        try:
            print("tin:", args.get('tin_url'))
            time1 = time.time()
            random_substances = SubstanceModel.get_random3(random)

            time2 = time.time()
            strtime1 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time1))
            strtime2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time2))
            print('{:s} !!!!!!!!!! started at {} and finished at {}. It took {:.3f} s'.format(args.get('tin_url'),
                                                                                              strtime1, strtime2,
                                                                                              (time2 - time1) % 60))

            if args.get('output_fields'):
                outputs = args.get('output_fields').replace(' ', '').split(',')
                json_ids = [sub.json_ids() for sub in random_substances]
                data = [{k: v for k, v in d.items() if k in outputs} for d in json_ids]
            else:
                data = [sub.json_ids() for sub in random_substances]

            if data:
                return jsonify(data)

        except Exception as e:
            print("Exception!!!!!!!!!!: ", args.get('tin_url'), " error:", e)
        return {'message': 'Not found'}, 404


class SubstanceRandom(Resource):
    def get(self, file_type=None):
        parser.add_argument('count', type=int)
        parser.add_argument('timeout', type=int)
        parser.add_argument('output_fields', type=str)
        args = parser.parse_args()
        return self.getRandom(args, file_type)

    def post(self, file_type=None):
        parser.add_argument('count', type=int)
        parser.add_argument('timeout', type=int)
        parser.add_argument('output_fields', type=str)
        args = parser.parse_args()
        return self.getRandom(args, file_type)

    @classmethod
    def getRandom(cls, args, file_type=None):
        requested_count = int(args.get('count'))
        timeout = 1
        if args.get('timeout'):
            timeout = args.get('timeout')
        output_fields = ""
        if args.get('output_fields'):
            output_fields = args.get('output_fields')

        tin_urls = get_all_unique_tin_servers()
        print("tin_urls", tin_urls)
        server_len = len(tin_urls)
        print("round(requested_count / server_len) ", round(requested_count / server_len))
        per_server_count = int(requested_count / server_len) + 100
        print("requested_count", requested_count)

        url = 'https://{}/subrandom'.format(request.host)
        result_list = []
        max_try = 100

        while len(result_list) < requested_count and max_try > 0:
            max_try -= 1
            params = {'tin_url': random.choice(tin_urls), 'random': per_server_count,
                      'output_fields': output_fields}

            try:
                print(params)
                uResponse = requests.post(url, params=params, timeout=timeout)
                dl = json.loads(uResponse.text)
                if dl and len(dl) > 0 and dl[0].get('smiles'):
                    result_list.extend(dl)
            except Exception as e:
                print("Exception", e)
            print("Current collected results ********************************************************* :",
                  len(result_list))
            print("Requested amount ********************************************************* :", requested_count)

        data = defaultdict(list)
        data['items'] = list(result_list)

        if not data['items']:
            return {'message': 'Not found'}, 404

        str_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        if file_type == 'csv':
            keys = list(data['items'][0].keys())
            return send_csv(data['items'][:requested_count], "substance_search_{}.csv".format(str_time), keys)
        elif file_type == 'txt':
            Formatter = OBJECT_MIMETYPE_TO_FORMATTER["text/plain"]
            keys = list(data['items'][0].keys())
            formatter = Formatter(fields=keys)
            ret_list = ""
            for line in formatter(data['items'][:requested_count]):
                ret_list += line

            download_filename = "search_{}.txt".format(str_time)
            response = make_response(ret_list, 200)
            response.mimetype = "text/plain"
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
            return response
        else:
            return jsonify(data)
