from flask_restful import Resource
from api.data.models.port_number import PortNumberModel

class PortNumberList(Resource):
    def get(self):
        return {'port_number': [x.json() for x in PortNumberModel.query.all()]}