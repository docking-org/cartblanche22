from flask_restful import Resource, reqparse
from app.data.models.tin.substance import SubstanceModel
from werkzeug.datastructures import FileStorage
from app.helpers.validation import base10, getTINUrl
from flask import jsonify, current_app, request
import requests
from collections import defaultdict
import grequests
import json

parser = reqparse.RequestParser()


class SubstanceList(Resource):
    def post(self, file_type=None):
        parser.add_argument('zinc_id-in', type=str)
        args = parser.parse_args()
        zinc_ids = args.get('zinc_id-in').split(',')  
        args['zinc_id-in'] = zinc_ids
        return self.getList(args, file_type)

    @classmethod
    def getList(cls, args, file_type=None):
        zinc_ids = args.get('zinc_id-in')  

        dict_ids = defaultdict(list)
        prev_url = ""
        prev_vals = ""
        for zinc_id in zinc_ids:
            if zinc_id:
                if prev_vals != zinc_id[4:6]:
                    url = getTINUrl(zinc_id)
                    prev_url = url
                    prev_vals = zinc_id[4:6]
                else:
                    url = prev_url
                dict_ids[url].append(base10(zinc_id))


        url = 'http://{}/substance'.format(request.host)
        for k, v in dict_ids.items():
            print(k)

        resp = (grequests.post(url, data={'sub_ids':','.join([str(i) for i in v]), 'tin_url':k}) for k, v in dict_ids.items())
        data = defaultdict(list)
        data['items'].extend([json.loads(res.text) for res in grequests.map(resp) if 'Not found' not in res.text])

        if not data['items']:
            return {'message': 'Not found'}, 404

        data['items'] = data['items'][0]
        return jsonify(data)


class Substance(Resource):
    def post(self):
        parser.add_argument('sub_ids', type=str)
        parser.add_argument('tin_url', type=str)
        args = parser.parse_args()

        sub_ids = args.get('sub_ids').split(',') 
        current_app.config['TIN_URL'] = args.get('tin_url')

        substances = SubstanceModel.query.filter(SubstanceModel.sub_id.in_(sub_ids)).all()

        data = [sub.json() for sub in substances]

        if data:
            return jsonify(data)
        return {'message': 'Not found'}, 404


class Substances(Resource): 
    def post(self, file_type=None):
        parser.add_argument('zinc_id-in', location='files', type=FileStorage, required=True)
        args = parser.parse_args()

        uploaded_file = args.get('zinc_id-in').stream.read().decode("latin-1")

        lines = uploaded_file.split('\n')
        args['zinc_id-in'] = lines

        return SubstanceList.getList(args, file_type)
        
    

