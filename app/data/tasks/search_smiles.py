import subprocess
from app.main import application

from app.main.search import search_byzincid
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, reqparse

from app.data.resources.substance import SubstanceList
from flask import render_template, request, json, jsonify, flash, Flask, redirect,g 

from app.data.models.tranche import TrancheModel

from app.helpers.representations import OBJECT_MIMETYPE_TO_FORMATTER
from flask import jsonify, current_app, request, make_response
from collections import defaultdict
from app.data.resources.substance import SubstanceModel
from flask_csv import send_csv
from datetime import datetime
import re

from app import celery_worker
from app.celery_worker import celery, flask_app, db
from celery.result import AsyncResult
from app.email_send import send_search_log


@application.route('/search/result_smiles', methods=['GET'])
def smiles_result():
    if request.method == 'GET':
        data = request.args.get("task")
        task= AsyncResult(data)
        
        data = task.get()
        print(data)
             
        if len(data) == 0:
            return render_template('errors/search404.html', href='/search/search_byzincid', header="We didn't find those molecules in the Zinc22 database. Click here to return"), 404
        return render_template('search/result_smiles.html', data_json=data, data=data)

class SearchSmiles(Resource):
    def post(self):
        data = request.form['smilesTextarea']
        file = request.files['smilesfile'].read().decode("utf-8")
        dist = request.form['dist']
        adist = request.form['adist']
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        fileDataList = file.split('\n')
        files = {
            'smiles-in': ','.join(textDataList + fileDataList),
            'dist': dist,
            'adist': adist,
        }
               
        task = search.delay(args=files)

        
        return redirect(('search/result_smiles?task={task}'.format(task = task.id)))

@celery.task
def search(args, file_type=None):   
    smilelist = args['smiles-in']
    dist = args['dist']
    adist = args['adist']

    res = subprocess.Popen("SWDIR=/nfs/db3/private_smallworld_4th_gen/ java -jar /home/s_jcastanon/smallworld-java/sw.jar" \
                           "sim -db /nfs/db3/private_smallworld_4th_gen/maps/zinc22-All.smi.anon.map -v -n0 -d {dist} -lup 0 -ldn 0" \
                           "-tup 0 -tdn 0 -rup 0 -rdn 0 -score AtomAlignment:SMILES {smiles}".format(smiles=smilelist, dist=dist), shell=True, stdout=subprocess.PIPE)
    result = res.stdout.read()
    print(result)
    result = result.split('\n')
    hits = []
    for line in result:
        if 'ZINC' in line:
            data = {}
            row = line.split(' ')
            data['hitMappedSmiles'] = row[3]
            data['zinc_id'] = row[4]
            hits.append(data)
    
    print(hits)

    return hits