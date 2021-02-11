from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from app.data.models.tranche import TrancheModel
from app.data.models.tin.substance import SubstanceModel
from app.helpers.validation import base10
from flask import jsonify, redirect, current_app, request
from flask_csv import send_csv
from app.helpers.validation import getTINUrl
import re
import json
import requests
import grequests
from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor
from requests import Session
from requests_futures.sessions import FuturesSession
import time

# def response_hook(resp, *args, **kwargs):
#     print("response hook!!!!!")
#     print("status.code:", resp.status_code)
#     if resp.text.strip().startswith("data"):
#         print("starts with data")
#         print("resp.text:", resp.text)
#         resp.data = json.loads(resp.text.split('\n\n')[0].strip("data:"))
#     else:
#         print("not start with data")
#         print("resp.text:", resp.text)
#         if resp.text.strip().startswith("<html"):
#             resp.data = "error"
#         else:
#             resp.data = json.loads(resp.text.split('\n\n')[0])
    #resp.data = resp.json()

parser = reqparse.RequestParser()
session = FuturesSession(executor=ProcessPoolExecutor(max_workers=10),
                         session=Session())
# session.hooks['response'] = response_hook


class Search(Resource):
    # def getDataByID(self, args, file_type=None):
    #     zinc_id = args.get('zinc_id')
    #     sub_id = base10(zinc_id)
    #     output_fields = []
    #     data = SubstanceModel.find_by_sub_id(sub_id)
    #     if data is None:
    #         return {'message': 'Substance not found with sub_id: {}'.format(sub_id)}, 404
    #
    #     if file_type == 'csv':
    #         keys = data.json().keys()
    #         return send_csv([data.json()], "search.csv", keys)
    #     else:
    #         data = data.json()
    #         if 'output_fields' in args and args.get('output_fields'):
    #             output_fields = args.get('output_fields').split(',')
    #             new_dict = { output_field: data[output_field] for output_field in output_fields }
    #             data = new_dict
    #
    #     tranche_args = {'mwt': zinc_id[4:5], 'logp': zinc_id[5:6]}
    #
    #     trancheQuery = TrancheModel.query
    #     tranche = trancheQuery.filter_by(**tranche_args).first()
    #
    #     data['tranche'] = tranche.to_dict()
    #     data['zinc_id'] = zinc_id
    #
    #     return jsonify(data)

    def getDataByID(self, args, file_type=None):
        zinc_id = args.get('zinc_id')
        tin_url = args.get('tin_url')
        url = 'http://{}/substance'.format(request.host)

        params = {'sub_ids': base10(zinc_id), 'tin_url': tin_url}
        print("url:", url, " params:", params)
        try:
            uResponse = requests.post(url, params=params)
            Jresponse = uResponse.text
            data = json.loads(Jresponse)
        except requests.ConnectionError:
            print("Connection Error")
            raise ConnectionError("Connection Error")

        if data:
            data[0]['zinc_id'] = zinc_id

        return data

    def get(self, file_type=None):
        parser.add_argument('output_fields', type=str)
        parser.add_argument('zinc_id', type=str)
        args = parser.parse_args()

        # Passing tin_url to change tin database in below function
        # @app.before_request
        # def before_request_callback():
        tin_url = getTINUrl(args.get('zinc_id'))
        args['tin_url'] = tin_url

        return self.getDataByID(args, file_type)

    def post(self, file_type=None):
        parser.add_argument('output_fields', type=str)
        parser.add_argument('zinc_id', type=str)
        args = parser.parse_args()
        new_args = {key: val for key, val in args.items() if val is not None}

        # Passing tin_url to change tin database in below function
        # @app.before_request
        # def before_request_callback():
        tin_url = getTINUrl(args.get('zinc_id'))
        new_args['tin_url'] = tin_url

        return self.getDataByID(new_args, file_type)




class SmileList(Resource):
    # def get(self, file_type=None):
    #     parser.add_argument('smiles-in', type=str)
    #     args = parser.parse_args()

    #     return self.getDataBySmiles(args, file_type)

    def post(self, file_type=None):
        parser.add_argument('smiles-in', type=str)
        parser.add_argument('dist', type=int)
        args = parser.parse_args()
        new_args = {key: val for key, val in args.items() if val is not None}
        smiles = new_args.get('smiles-in').split(',')
        new_args['smiles-in'] = smiles

        return self.getList(new_args, file_type)

    @classmethod
    def getList(self, args, file_type=None):
        smiles = filter(None, args.get('smiles-in'))
        dist = 0
        if 'dist' in args:
            dist = args.get('dist')


        uri = "{}/search/submit".format(current_app.config['ZINC_SMALL_WORLD_SERVER'])
        params = {
            'smi': '',
            'db': 'zinc22_2d_All.smi.anon',
            'dist': dist,
            'tdn': 4,
            'tup': 4,
            'rdn': 4,
            'rup': 4,
            'ldn': 4,
            'lup': 4,
            'maj': 4,
            'min': 4,
            'sub': 4,
            'scores': 'Atom Alignment,ECFP4,Daylight'
        }

        futures = []
        for smile in smiles:
            params['smi'] = smile
            print(smile, uri)
            future = session.get(uri, params=params, auth=('gpcr', 'xtal'), stream=True)
            # future.i = i
            futures.append(future)

        hlids = []
        for future in as_completed(futures):
            resp = future.result()
            try:
                data = json.loads(resp.text.split('\n\n')[0].strip("data:"))
            except Exception as e:
                print("Exception DATA:>>>>>>>>>>>>")
                print(resp.text)
                continue
            print(data['hlid'])
            hlids.append(data['hlid'])

        result = self.get_result_from_smallworld(file_type, hlids)
        return result


    @classmethod
    def get_result_from_smallworld(cls, type_, hlids, start=0, length=100, cutoff=0.0):
        uri = "{}/search/view".format(current_app.config['ZINC_SMALL_WORLD_SERVER'])

        params = {
            'hlid': 0,
            'columns[0][data]': 0,
            'columns[0][name]': 'alignment',
            'columns[0][searchable]': 'true',
            'columns[0][orderable]': 'false',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': 1,
            'columns[1][name]': 'dist',
            'columns[1][searchable]': 'true',
            'columns[1][orderable]': 'true',
            'columns[1][search][value]': '0-4',
            'columns[1][search][regex]': 'false',
            'columns[2][data]': 2,
            'columns[2][name]': 'ecfp4',
            'columns[2][searchable]': 'true',
            'columns[2][orderable]': 'true',
            'columns[2][search][value]': '',
            'columns[2][search][regex]': 'false',
            'columns[3][data]': 3,
            'columns[3][name]': 'daylight',
            'columns[3][searchable]': 'true',
            'columns[3][orderable]': 'true',
            'columns[3][search][value]': '',
            'columns[3][search][regex]': 'false',
            'columns[4][data]': 4,
            'columns[4][name]': 'topodist',
            'columns[4][searchable]': 'true',
            'columns[4][orderable]': 'true',
            'columns[4][search][value]': '0-4',
            'columns[4][search][regex]': 'false',
            'columns[5][data]': 5,
            'columns[5][name]': 'mces',
            'columns[5][searchable]': 'true',
            'columns[5][orderable]': 'true',
            'columns[5][search][value]': '',
            'columns[5][search][regex]': 'false',
            'columns[6][data]': 6,
            'columns[6][name]': 'tdn',
            'columns[6][searchable]': 'true',
            'columns[6][orderable]': 'true',
            'columns[6][search][value]': '0-4',
            'columns[6][search][regex]': 'false',
            'columns[7][data]': 7,
            'columns[7][name]': 'tup',
            'columns[7][searchable]': 'true',
            'columns[7][orderable]': 'true',
            'columns[7][search][value]': '0-4',
            'columns[7][search][regex]': 'false',
            'columns[8][data]': 8,
            'columns[8][name]': 'rdn',
            'columns[8][searchable]': 'true',
            'columns[8][orderable]': 'true',
            'columns[8][search][value]': '0-4',
            'columns[8][search][regex]': 'false',
            'columns[9][data]': 9,
            'columns[9][name]': 'rup',
            'columns[9][searchable]': 'true',
            'columns[9][orderable]': 'true',
            'columns[9][search][value]': '0-4',
            'columns[9][search][regex]': 'false',
            'columns[10][data]': 10,
            'columns[10][name]': 'ldn',
            'columns[10][searchable]': 'true',
            'columns[10][orderable]': 'true',
            'columns[10][search][value]': '0-4',
            'columns[10][search][regex]': 'false',
            'columns[11][data]': 11,
            'columns[11][name]': 'lup',
            'columns[11][searchable]': 'true',
            'columns[11][orderable]': 'true',
            'columns[11][search][value]': '0-4',
            'columns[11][search][regex]': 'false',
            'columns[12][data]': 12,
            'columns[12][name]': 'mut',
            'columns[12][searchable]': 'true',
            'columns[12][orderable]': 'true',
            'columns[12][search][value]': '',
            'columns[12][search][regex]': 'false',
            'columns[13][data]': 13,
            'columns[13][name]': 'maj',
            'columns[13][searchable]': 'true',
            'columns[13][orderable]': 'true',
            'columns[13][search][value]': '0-4',
            'columns[13][search][regex]': 'false',
            'columns[14][data]': 14,
            'columns[14][name]': 'min',
            'columns[14][searchable]': 'true',
            'columns[14][orderable]': 'true',
            'columns[14][search][value]': '0-4',
            'columns[14][search][regex]': 'false',
            'columns[15][data]': 15,
            'columns[15][name]': 'hyb',
            'columns[15][searchable]': 'true',
            'columns[15][orderable]': 'true',
            'columns[15][search][value]': '0-4',
            'columns[15][search][regex]': 'false',
            'columns[16][data]': 16,
            'columns[16][name]': 'sub',
            'columns[16][searchable]': 'true',
            'columns[16][orderable]': 'true',
            'columns[16][search][value]': '0-4',
            'columns[16][search][regex]': 'false',
            'order[0][column]': 2,
            'order[0][dir]': 'asc',
            'start': start,
            'length': length,
            'search[value]': '',
            'search[regex]': 'false',
        }

        ret_data = cls.request_uri(uri, hlids, params)
        return ret_data

    @classmethod
    def request_uri(cls, uri, hlids, params, *count):
        futures = []
        for hlid in hlids:
            params['hlid'] = hlid
            future = session.get(uri, params=params, auth=('gpcr', 'xtal'))
            futures.append(future)

        # time.sleep(3)
        result = []
        for future in as_completed(futures):
            try:
                resp = future.result()
                print("statuscode:", resp.status_code)
                print("resp.text:", resp.text)
                data = json.loads(resp.text.split('\n\n')[0])
            except Exception as e:
                print("Exception:", e)
                print(resp.text)
                continue

            for dt in data['data']:
                res = {}
                res['qrySmiles'] = dt[0]['qrySmiles']
                res['zinc_id'] = dt[0]['id']
                res['score'] = round(float(dt[2]), 2)
                res['qryMappedSmiles'] = dt[0]['qryMappedSmiles']
                res['hitMappedSmiles'] = dt[0]['hitMappedSmiles']
                result.append(res)

        if not result and not count:
            print("result was empty !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            cls.request_uri(uri, hlids, params, 1)

        return result



class Smiles(Resource):
    def post(self, file_type=None):
        parser.add_argument('smiles-in', location='files', type=FileStorage, required=True)
        parser.add_argument('dist', type=int)
        args = parser.parse_args()
        new_args = {key: val for key, val in args.items() if val is not None}

        uploaded_file = new_args.get('smiles-in').stream.read().decode("latin-1")

        lines = uploaded_file.split('\n')
        new_args['smiles-in'] = lines

        return SmileList.getList(new_args, file_type)