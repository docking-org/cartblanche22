from flask import Response
from app.main import application

@application.route('/res', methods= ['GET'])
def res():
    xml = '<foo>saokmlda</foo>'
    print(xml)
    return Response(xml, mimetype='text/xml')