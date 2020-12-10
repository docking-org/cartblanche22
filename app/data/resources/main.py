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

parser = reqparse.RequestParser()


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

   




    