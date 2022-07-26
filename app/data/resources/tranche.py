from flask_restful import Resource, reqparse
from app.data.models.tranche import TrancheModel
from app.data.models.server_mapping import ServerMappingModel
from app.data.models.ip_address import IPAddressModel

from flask import jsonify

parser = reqparse.RequestParser()


class Tranches(Resource):
    def getData(self, file_type=None):
        parser.add_argument('mwt', type=str)
        parser.add_argument('logp', type=str)
        parser.add_argument('sum', type=str)
        parser.add_argument('last', type=str)
        parser.add_argument('ip', type=str)

        args = parser.parse_args()
        new_args = {key: val for key, val in args.items() if val is not None}

        tranche_query = TrancheModel.query

        if new_args.get('ip'):
            tranche_query = tranche_query.filter(TrancheModel.server_mapping.has(
                ServerMappingModel.ip_address.has(IPAddressModel.ip == new_args.get('ip'))))
            new_args.pop('ip')

        data = tranche_query.filter_by(**new_args).all()

        # if file_type:
        #     return Response(str(data),
        #                     mimetype='application/json',
        #                     headers={'Content-Disposition': '
        #                     attachment;filename=slices.json'})

        data = {'items': [x.to_dict() for x in data]}
        return jsonify(data)

    def get(self, file_type=None):
        return self.getData(file_type)
    
    def post(self, file_type=None):
        return self.getData(file_type)