

from app.data.models.tin.substance import SubstanceModel
from config import Config

import app
import random
from app.main import application
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, reqparse
from app.celery_worker import celery, flask_app, db
from celery.execute import send_task
from flask import render_template, request

from app.helpers.validation import base62
from flask import jsonify, current_app, request, make_response
from flask_csv import send_csv
import time
import pandas as pd


from app.celery_worker import celery, flask_app, db
from celery.result import AsyncResult
import psycopg2

class GetRandomMolecules(Resource):
    def post(self, file_type=None):
        if not request.form:
            data= request.data.decode().split(',')
            count = data[0]
            file_type = data[1]
        else:
            count = request.form['count']
        result = []
        try:
            task = getRandom.delay(count, file_type)
            result = task.get()
           
        except Exception as e:
            print(e)
        return result


@celery.task
def getRandom(count, file_type = None, timeout=10):
    logp_range="M500 M400 M300 M200 M100 M000 P000 P010 P020 P030 P040 P050 P060 P070 P080 P090 P100 P110 P120 P130 P140 P150 P160 P170 P180 P190 P200 P210 P220 P230 P240 P250 P260 P270 P280 P290 P300 P310 P320 P330 P340 P350 P360 P370 P380 P390 P400 P410 P420 P430 P440 P450 P460 P470 P480 P490 P500 P600 P700 P800 P900".split(" ")
    logp_range={e:i for i, e in enumerate(logp_range)}
    
    total = 0
    result = []
    limit = int(count)/10
    dbcount = 0
    while total < int(count):
        ip = random.choice(list(app.Config.SQLALCHEMY_BINDS))
        if ip.replace(".",'').replace(':','').isnumeric():
            dbcount+=1
            print(ip)
            tstart = time.time()
            url = app.Config.SQLALCHEMY_BINDS[ip]
            url = url.replace('+psycopg2', '')
            try:
                conn = psycopg2.connect(url, connect_timeout=timeout)
                curs = conn.cursor()
                curs.execute('select max(sub_id) from substance;')
                max = curs.fetchone()[0]
                
                curs.execute(
                    ("select * from substance LEFT JOIN tranches ON substance.tranche_id = tranches.tranche_id where sub_id > random() * {max} limit {limit};").format(max=max, limit = limit)
                )
                
                res = curs.fetchall()
                result.append(res)
                total += len(res)
                conn.close()
            except:
                print('')
    print(("retrieved {count} results across {dbcount} databases").format(count = total, dbcount= dbcount))
    results = []         
    
    for dbresult in result:
        for i in dbresult:
            molecule= {}
            tranche = i[7]
            if(tranche):
                sub = base62(int(i[0]))
                h = base62(int(tranche[1:3]))
                p = base62(logp_range[tranche[3:]])
                molecule['tranche'] = tranche
    
            else:
                molecule['tranche'] = "None"
            sub = (10 - len(sub)) * "0" + sub
            molecule['zincid'] = "ZINC" + h + p + sub
            molecule['SMILES'] = i[1]
            
            results.append(molecule)
    
    if(file_type == "csv"):
        res = pd.DataFrame(results)
        return res.to_csv(encoding='utf-8', index=False)
    elif(file_type == "txt"):
        res = pd.DataFrame(results)
        return res.to_csv(encoding='utf-8', index=False, sep=" ")
        
    return results
            
#  tstart = time.time()
#     conn = psycopg2.connect(dsn, connect_timeout=timeout)
#     curs = conn.cursor()