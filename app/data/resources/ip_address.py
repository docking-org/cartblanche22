from flask_restful import Resource
from api.data.models.ip_address import IPAddressModel

class IPAddressList(Resource):
    def get(self):
        return {'ip_address': [x.json() for x in IPAddressModel.query.all()]}
        