from flask_restful import Resource, reqparse
from app.data.models.tin.substance import SubstanceModel
from app.data.models.server_mapping import ServerMappingModel
from app.data.models.tranche import TrancheModel
from werkzeug.datastructures import FileStorage
from app.helpers.validation import base10, getTINUrl
from flask import jsonify, current_app, request
import requests
from collections import defaultdict
import grequests
import json
import time
from flask_csv import send_csv
from datetime import datetime
from sqlalchemy import func

parser = reqparse.RequestParser()


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
        zinc_ids = args.get('zinc_id-in')  
        output_fields = args.get('output_fields')
        dict_ids = defaultdict(list)
        dict_subid_zinc_id = defaultdict(list)
        prev_url = ""
        prev_vals = ""
        overlimit_count = 0
        chunk = 2000
        if args.get('chunk'):
            chunk = args.get('chunk')

        for zinc_id in zinc_ids:
            if zinc_id:
                if prev_vals != zinc_id[4:6]:
                    url = getTINUrl(zinc_id)
                    if not url:
                        return {'message': 'No server is mapped to {}. Please contact with Irwin Lab.'.format(zinc_id)}, 404
                    prev_url = url
                    prev_vals = zinc_id[4:6]
                else:
                    url = prev_url

                if len(dict_ids[url]) > chunk:
                    dict_ids["{}-{}".format(url, overlimit_count)] = dict_ids[url]
                    dict_ids[url] = [base10(zinc_id)]
                    overlimit_count += 1
                else:
                    dict_ids[url].append(base10(zinc_id))
                dict_subid_zinc_id[int(base10(zinc_id))].append(zinc_id)


        url = 'http://{}/substance'.format(request.host)
        for k, v in dict_ids.items():
            print("TIN URLS ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print(k, len(v))

        resp = (grequests.post(url,
                               data={
                                   'sub_ids':','.join([str(i) for i in v]),
                                   'tin_url':k.split('-')[0],
                                   'output_fields': output_fields
                               }, timeout=15) for k, v in dict_ids.items())

        data = defaultdict(list)
        data['items'].extend([json.loads(res.text) for res in grequests.map(resp) if res and 'Not found' not in res.text])

        for dt in data['items']:
            for d in dt:
                if not args.get('output_fields') or 'zinc_id' in output_fields:
                    d['zinc_id'] = dict_subid_zinc_id.get(d.get('sub_id'))[0]
                    if not args.get('output_fields') or 'sub_id' not in output_fields:
                        d.pop('sub_id')
                    if not args.get('output_fields') or 'tranche' in output_fields:
                        tranche_args = {'mwt': d['zinc_id'][4:5], 'logp': d['zinc_id'][5:6]}

                        trancheQuery = TrancheModel.query
                        tranche = trancheQuery.filter_by(**tranche_args).first()

                        d['tranche'] = tranche.to_dict()

        if not data['items']:
            return {'message': 'Not found'}, 404

        data['items'] = data['items'][0]

        if file_type in ['csv', 'txt']:
            keys = list(data['items'][0].keys())
            str_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            return send_csv(data['items'], "zinc_id_search_{}.csv".format(str_time), keys)
        else:
            return jsonify(data)


class Substance(Resource):
    def post(self, file_type=None):
        parser.add_argument('sub_ids', type=str)
        parser.add_argument('tin_url', type=str)
        parser.add_argument('output_fields', type=str)
        args = parser.parse_args()

        sub_ids = (int(id) for id in args.get('sub_ids').split(','))
        print("REQUESTED TIN_URL from Substance POST", args.get('tin_url'))
        time1 = time.time()
        substances = SubstanceModel.query.filter(SubstanceModel.sub_id.in_(sub_ids)).all()

        time2 = time.time()
        print('{:s} !!!!!!!!!! function took {:.3f} ms'.format(args.get('tin_url'), (time2 - time1) * 1000.0))

        if substances is None:
            return {'message': 'Substance not found with sub_id(s): {}'.format(sub_ids)}, 404

        # data = [sub.json() for sub in substances]
        data = []
        for sub in substances:
            data_dict = sub.json()
            if 'output_fields' in args and args.get('output_fields'):
                output_fields = args.get('output_fields').split(',')
                # sub_id will need for generating zinc_id in different function
                if 'sub_id' not in output_fields:
                    output_fields.append('sub_id')

                # Removing zinc_id and it is gonna add in different function
                output_fields.remove('zinc_id')
                new_dict = {output_field: data_dict[output_field] for output_field in output_fields }
                data_dict = new_dict
            data.append(data_dict)

        if data:
            return jsonify(data)
        return {'message': 'Not found'}, 404


class Substances(Resource): 
    def post(self, file_type=None):
        parser.add_argument('zinc_id-in', location='files', type=FileStorage, required=True)
        parser.add_argument('chunk', type=int)
        parser.add_argument('output_fields', type=str)
        args = parser.parse_args()

        uploaded_file = args.get('zinc_id-in').stream.read().decode("latin-1")

        lines = uploaded_file.split('\n')
        args['zinc_id-in'] = lines

        return SubstanceList.getList(args, file_type)


class SubstanceRandomList(Resource):
    def post(self, file_type=None):
        parser.add_argument('random', type=str)
        parser.add_argument('tin_url', type=str)
        args = parser.parse_args()
        random = args.get('random')

        try:
            print("tin:", args.get('tin_url'))
            time1 = time.time()
            # random_substances = SubstanceModel.query.order_by(func.random()).limit(random)
            # random_substances = SubstanceModel.query.offset(func.floor(func.random() * SubstanceModel.query.count())).limit(random)
            random_substances = SubstanceModel.get_random(random)

            time2 = time.time()
            print('{:s} !!!!!!!!!! function took {:.3f} ms'.format(args.get('tin_url'), (time2 - time1) * 1000.0))

            data = [sub.json_ids() for sub in random_substances]
            if data:
                return jsonify(data)

        except Exception as e:
            print("Exception!!!!!!!!!!: ", args.get('tin_url'), " error:", e)
        return {'message': 'Not found'}, 404


class SubstanceRandom(Resource):
    def get(self, file_type=None):
        parser.add_argument('count', type=str)
        args = parser.parse_args()
        return self.getRandom(args, file_type)

    def post(self, file_type=None):
        parser.add_argument('count', type=str)
        args = parser.parse_args()
        return self.getRandom(args, file_type)

    @classmethod
    def getRandom(cls, args, file_type=None):
        count = int(args.get('count'))

        server_mappings = ServerMappingModel.query.distinct(
            ServerMappingModel.ip_fk,
            ServerMappingModel.port_fk).all()

        per_server_count = int(round(count / len(server_mappings))) + 100

        tin_urls = {}
        tin_list = []
        for sm in server_mappings:
            if sm.tranches:
                url = "{}:{}".format(sm.ip_address.ip, sm.port_number.port)
                tin_list.append(url)
                tin_urls[url] = "ZINC{}{}".format(sm.tranches[0].mwt, sm.tranches[0].logp)

        url = 'http://{}/subrandom'.format(request.host)
        resp = (grequests.post(url, data={'tin_url': k, 'random': per_server_count}, timeout=15) for
                k, v in tin_urls.items())

        data = defaultdict(list)
        data['items'].extend([json.loads(res.text) for res in grequests.map(resp) if res and 'Not found' not in res.text])

        if not data['items']:
            return {'message': 'Not found'}, 404

        data['items'] = data['items'][0]

        if file_type in ['csv', 'txt']:
            keys = list(data['items'][0].keys())
            str_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            return send_csv(data['items'], "substance_search_{}.csv".format(str_time), keys)
        else:
            return jsonify(data)

        return None

