from flask import jsonify, session
from app.main import application

@application.route('/deleteSession', methods=['GET'])
def deleteSession():
    session.clear()
    return jsonify('deleted')