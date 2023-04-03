from flask import jsonify, session
from cartblanche.app import app 

@app.route('/deleteSession', methods=['GET'])
def deleteSession():
    session.clear()
    return jsonify('deleted')