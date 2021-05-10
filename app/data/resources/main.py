from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from app.data.resources.substance import SubstanceList
from app.helpers.representations import OBJECT_MIMETYPE_TO_FORMATTER
from flask import jsonify, redirect, current_app, request, make_response
from flask_csv import send_csv
import json
import itertools
from itertools import repeat
import requests
import time
from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from requests import Session
from requests_futures.sessions import FuturesSession
from datetime import datetime

parser = reqparse.RequestParser()
session = FuturesSession(executor=ProcessPoolExecutor(max_workers=10),
                         session=Session())


# session.hooks['response'] = response_hook


class Search(Resource):
    def getDataByID(self, args, file_type=None):
        zinc_id = args.get('zinc_id')
        args['zinc_id-in'] = [zinc_id]
        return SubstanceList.getList(args, file_type)

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
    def post(self, file_type=None):
        parser.add_argument('smiles-in', type=str)
        parser.add_argument('adist', type=int)
        parser.add_argument('dist', type=int)
        args = parser.parse_args()
        new_args = {key: val for key, val in args.items() if val is not None}
        smiles = new_args.get('smiles-in').split(',')
        new_args['smiles-in'] = smiles

        return self.getList(new_args, file_type)

    @classmethod
    def getList(self, args, file_type=None):
        smiles = filter(None, args.get('smiles-in'))
        adist = 2
        if 'adist' in args:
            adist = args.get('adist')

        dist = 4
        if 'dist' in args:
            dist = args.get('dist')

        uri = "{}/search/submit".format(current_app.config['ZINC_SMALL_WORLD_SERVER'])
        hlids = self.get_hlids(smiles, repeat(uri), repeat(adist))
        result = self.get_result_from_smallworld(file_type, hlids, dist)

        flat_list = itertools.chain.from_iterable(result)
        filtered_result = [r for r in flat_list if r]

        str_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        if file_type == 'csv':
            keys = list(filtered_result[0].keys())
            return send_csv(filtered_result, "smiles_search_{}.csv".format(str_time), keys)
        elif file_type == 'txt':
            Formatter = OBJECT_MIMETYPE_TO_FORMATTER["text/plain"]
            keys = list(filtered_result[0].keys())
            formatter = Formatter(fields=keys)
            ret_list = ""
            for line in formatter(filtered_result):
                ret_list += line

            download_filename = "search_{}.txt".format(str_time)
            response = make_response(ret_list, 200)
            response.mimetype = "text/plain"
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
            return response
        else:
            return filtered_result

    @classmethod
    def get_hlids(cls, smiles, uri, adist):
        with ThreadPoolExecutor(max_workers=3) as executor:
            return executor.map(cls.get_hlid, smiles, uri, adist, timeout=60)

    @classmethod
    def get_hlid(cls, smile, uri, adist):
        params = {
            'smi': smile,
            'db': 'zinc_2d_All.smi.anon',
            'dist': adist,
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

        length = 4
        try:
            time1 = time.time()
            from contextlib import closing
            with closing(requests.get(uri, params=params, auth=('gpcr', 'xtal'), stream=True,
                                      headers={'Connection': 'close'}, timeout=5)) as r:
                print(r.url)
                iterator = r.iter_lines()
                status_more_count = 0
                counts_to_wait_more = 1
                status_3 = 1
                if length > 1:
                    # how many times to wait MORE
                    counts_to_wait_more = length
                for n, l in enumerate(iterator, start=1):
                    first_line = l[5:]
                    if len(l) > 0:
                        status = json.loads(first_line)['status']
                        print(status)
                        if status == 'MORE':
                            if status_more_count > counts_to_wait_more:
                                r.close()
                                break
                            status_more_count += 1
                        if status == 'Ground Control to Major Tom' or status == 'END':
                            if status_3 > 4 or status == 'END':
                                r.close()
                                break
                            status_3 += 1
            print(first_line)
            data = json.loads(first_line)
            print(data)
        except requests.ConnectionError:
            print("Connection Error")
            return None
        except ValueError:
            print("Value Error")
            return None

        time2 = time.time()
        strtime1 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time1))
        strtime2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time2))
        print('SmallWorld submit request started at {} and finished at {}. It took {:.3f} s'.format(strtime1, strtime2, (time2 - time1) % 60))

        hlid = data['hlid']
        print(hlid)
        return hlid


    @classmethod
    def get_result_from_smallworld(cls, type_, hlids, dist=4, start=0, length=100):
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
            'columns[1][search][value]': '0-{}'.format(dist),
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

        ret_data = cls.request_uri_hlids(repeat(uri), hlids, repeat(params))
        return ret_data

    @classmethod
    def request_uri_hlids(cls, uri, hlids, params, *count):
        with ThreadPoolExecutor(max_workers=13) as executor:
            return executor.map(cls.request_uri_hlid, uri, hlids, params, timeout=60)

    @classmethod
    def request_uri_hlid(cls, uri, hlid, params):
        result = []
        try:
            params['hlid'] = hlid
            resp = requests.get(uri, params=params, auth=('gpcr', 'xtal'), stream=False)
            print("statuscode:", resp.status_code)
            print("resp.text:", resp.text)
            data = json.loads(resp.text.split('\n\n')[0])
            print("data:", data)
            for dt in data['data']:
                res = {}
                res['qrySmiles'] = dt[0]['qrySmiles']
                res['zinc_id'] = dt[0]['id']
                res['score'] = round(float(dt[2]), 2)
                res['qryMappedSmiles'] = dt[0]['qryMappedSmiles']
                res['hitMappedSmiles'] = dt[0]['hitMappedSmiles']
                result.append(res)

        except Exception as e:
            print("Exception:", e)
            print(resp.text)
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
        parser.add_argument('adist', type=int)
        parser.add_argument('dist', type=int)
        args = parser.parse_args()
        new_args = {key: val for key, val in args.items() if val is not None}

        uploaded_file = new_args.get('smiles-in').stream.read().decode("latin-1")

        lines = uploaded_file.split('\n')
        new_args['smiles-in'] = lines

        return SmileList.getList(new_args, file_type)
