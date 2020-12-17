from flask_restful import Resource, reqparse
from app.data.models.tranche import TrancheModel
from app.data.models.tin.substance import SubstanceModel
from app.helpers.validation import base10
from flask import jsonify, redirect
from flask_csv import send_csv
import re
from flask import current_app
import json 
import requests
import grequests
from concurrent.futures import as_completed
from pprint import pprint
from requests_futures.sessions import FuturesSession


parser = reqparse.RequestParser()
session = FuturesSession(max_workers=10)


class Search(Resource):
    def getDataByID(self, args, file_type=None):
        zinc_id = args.get('zinc_id')  
        sub_id = base10(zinc_id)
        output_fields = []
        data = SubstanceModel.find_by_sub_id(sub_id)
        if data is None:
            return {'message': 'Substance not found with sub_id: {}'.format(sub_id)}, 404


        if file_type == 'csv':
            keys = data.json().keys()
            return send_csv([data.json()], "search.csv", keys)
        else:
            data = data.json()
            if 'output_fields' in args and args.get('output_fields'):
                output_fields = args.get('output_fields').split(',')
                new_dict = { output_field: data[output_field] for output_field in output_fields }
                data = new_dict

        tranche_args = {}
        tranche_args['mwt'] = zinc_id[4:5]
        tranche_args['logp'] = zinc_id[5:6]
            
            
        trancheQuery = TrancheModel.query
        tranche = trancheQuery.filter_by(**tranche_args).first()

        data['tranche'] = tranche.to_dict()
        data['zinc_id'] = zinc_id
        
        return jsonify(data)

    def get(self, file_type=None):
        parser.add_argument('output_fields', type=str)
        parser.add_argument('zinc_id', type=str)
        args = parser.parse_args()
        
        return self.getDataByID(args, file_type)

    def post(self, file_type=None):
        parser.add_argument('output_fields', type=str)
        parser.add_argument('zinc_id', type=str)
        args = parser.parse_args()
        new_args = {key: val for key, val in args.items() if val is not None}
        
        return self.getDataByID(new_args, file_type)

   

class SmileList(Resource):
    # def get(self, file_type=None):
    #     parser.add_argument('smiles-in', type=str)
    #     args = parser.parse_args()
        
    #     return self.getDataBySmiles(args, file_type)


    def post(self, file_type=None):
        parser.add_argument('smiles-in', type=str)
        args = parser.parse_args()
        smiles = args.get('smiles-in').split(',')  
        args['smiles-in'] = smiles
        
        return self.getList(args, file_type)


    def getList(self, args, file_type=None):
        smiles = args.get('smiles-in')

        uri = "{}/search/submit".format(current_app.config['ZINC_SMALL_WORLD_SERVER'])
        params = {
            'smi': 'C1=CC=CC=C1',
            'db': 'zinc22_2d_All.smi.anon',
            'dist': 0,
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
            future = session.get(uri, params=params, auth=('gpcr', 'xtal'), stream=True)
            # future.i = i
            futures.append(future)

        hlids = []
        for future in as_completed(futures):
            resp = future.result()
            data = json.loads(resp.text.split('\n\n')[0][5:])
            hlids.append(data['hlid'])

        print(hlids)
        result = self.get_result_from_smallworld("type", hlids)

        return jsonify(result)


    @classmethod
    def get_result_from_smallworld(cls, type_, hlids, start=0, length=100, cutoff=0.0):
        scores = {}
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
            'order[0][dir]': 'desc',
            'start': start,
            'length': length,
            'search[value]': '',
            'search[regex]': 'false',
        }

        result_data = {}

        ret_data = cls.request_uri(uri, hlids, params)

        print(ret_data)
        
        return ret_data



    @classmethod
    def request_uri(cls, uri, hlids, params):
        try:
            futures = []
            for hlid in hlids:
                params['hlid'] = hlid
                future = session.get(uri, params=params, auth=('gpcr', 'xtal'), stream=False)

                futures.append(future)

            result = []
            for future in as_completed(futures):
                resp = future.result()
                result_data = json.loads(resp.text)
                
                for dt in result_data['data']:
                    res = {}
                    res['qrySmiles'] = dt[0]['qrySmiles']
                    res['zinc_id'] = dt[0]['id']
                    res['score'] = round(float(dt[2]), 2)
                    res['qryMappedSmiles'] = dt[0]['qryMappedSmiles']
                    res['hitMappedSmiles'] = dt[0]['hitMappedSmiles']
                    result.append(res)
                    
            return result

        except requests.ConnectionError:
            print("Connection Error")
            return None
        except ValueError:
            print("Value Error")
            return None

        return result


class Smiles(Resource): 
    def post(self, file_type=None):
        parser.add_argument('smiles-in', location='files', type=FileStorage, required=True)
        args = parser.parse_args()

        uploaded_file = args.get('smiles-in').stream.read().decode("latin-1")

        lines = uploaded_file.split('\n')
        args['smiles-in'] = lines

        return SmileList.getList(args, file_type)