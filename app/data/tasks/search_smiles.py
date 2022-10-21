import subprocess
import re
import os
import tempfile

from app.main import application

from app.main.search import search_byzincid
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, reqparse
from flask import render_template, request, json, jsonify, flash, Flask, redirect,g 
from flask import jsonify, current_app, request, make_response
from app import celery_worker
from app.celery_worker import celery, flask_app, db
from celery import group, chord
from celery.result import AsyncResult
from app.email_send import send_search_log
from app.data.tasks.search_zinc import getSubstanceList
from config import Config

@application.route('/search/result_smiles', methods=['GET'])
def smiles_result():
    if request.method == 'GET':
        data = request.args.get("task")
        task = AsyncResult(data)
        data = task.get()["found"]
       
        if len(data) == 0:
            return render_template('errors/search404.html', href='/search/search_byzincid', header="We didn't find those molecules in the Zinc22 database. Click here to return"), 404
        return render_template('search/result.html', data22=data, data20=[], missing22=[])

class SearchSmiles(Resource):
    def post(self):
        data = request.form['smilesTextarea']
        file = request.files['smilesfile'].read().decode("utf-8")
        dist = request.form['dist']
        adist = request.form['adist']
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        fileDataList = file.split('\n')
        files = {
            'smiles-in': '\n'.join(textDataList + fileDataList),
            'dist': dist,
            'adist': adist,
        }
        task = search.delay(files) 

        data = task.get()
        
        task = getSubstanceList.delay([], data)
        return redirect(('search/result?task={task}'.format(task = task.id)))

def curlSearch(files): 
    task = search.delay(files)
    data = task.get()
    task = getSubstanceList.delay([], data)
    print(task)
    data = task.get()
    return data

@celery.task
def formatIds(args):
    return args[0]

@celery.task
def search(args, file_type=None):   
    smilelist = args['smiles-in']
    dist = '2' if int(args['dist']) > 2 else args['dist'] 
    adist = '2' if int(args['adist']) > 2 else args['adist'] 
    
    result = []

    with tempfile.NamedTemporaryFile() as tmp:
        print(smilelist)
        tmp.write(smilelist.encode())
        tmp.flush()
        res = subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                            "sim -db "+ Config.SMALLWORLD_MAP_PATH + "/zinc22-All.smi.anon.map -v -n0 -d {adist} " \
                            "-score AtomAlignment:SMILES {smiles} | grep '={dist}'".format(smiles=tmp.name, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)
        out, err = res.communicate()
        result = out.decode().split('\n')
    hits = []
    for line in result:
        if 'ZINC' in line:
            data = {}
            row = line.split(' ')
            data['hitMappedSmiles'] = row[3]
            data['zinc_id'] = row[4]
            if data not in hits: 
                hits.append(data)

    ids = []
    for hit in hits:
        ids.append(hit['zinc_id'])
    
    return ids
