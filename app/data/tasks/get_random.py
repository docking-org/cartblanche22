

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

from app.helpers.validation import base62, get_conn_string
from flask import jsonify, current_app, request, make_response
from flask_csv import send_csv
import time
import pandas as pd
from app.data.models.tranche import TrancheModel

from app.celery_worker import celery, flask_app, db
from celery.result import AsyncResult
import psycopg2


class GetRandomMolecules(Resource):
    def post(self, file_type=None):
        count = request.form['count']
        if request.form.get('subset'):
            subset = request.form['subset']
        else:
            subset = None
        
        result = []
        print("here")
        if subset == "none":
            subset = None
    
        result = getRandom(subset, count, file_type)
        return result


@celery.task
def getRandom(subset, count, file_type = None, timeout=10):
    logp_range="M500 M400 M300 M200 M100 M000 P000 P010 P020 P030 P040 P050 P060 P070 P080 P090 P100 P110 P120 P130 P140 P150 P160 P170 P180 P190 P200 P210 P220 P230 P240 P250 P260 P270 P280 P290 P300 P310 P320 P330 P340 P350 P360 P370 P380 P390 P400 P410 P420 P430 P440 P450 P460 P470 P480 P490 P500 P600 P700 P800 P900".split(" ")
    logp_range={e:i for i, e in enumerate(logp_range)}
    
    total = 0
    result = []
    to_pull = int(count)
    dbcount = 0
    
    population, distribution = getDistribution(subset)    
    results = []       
    while to_pull > 0:
        db_map = {}
        for i in range(to_pull):
            url = random.choices(population, distribution)[0]
            if db_map.get(url):
                db_map[url] += 1
            else:
                db_map[url] = 1
            
        for url in db_map:
            limit = db_map[url]
            try:
                dbcount+=1
                print(url)
                tstart = time.time()
                
                conn = psycopg2.connect(url, connect_timeout=timeout)
                curs = conn.cursor()
                curs.execute('select max(sub_id) from substance;')
                max = curs.fetchone()[0]
                print(max)
                curs.execute(
                    ("select * from substance LEFT JOIN tranches ON substance.tranche_id = tranches.tranche_id where sub_id > random() * {max} limit {limit};").format(max=max, limit = limit)
                
                )
                
                res = curs.fetchall()
                print(res)
                result.append(res)
                total += len(res)
                conn.close()
            except:
                print()
        
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
                if len(results) < int(count):
                    results.append(molecule)
                
        to_pull = to_pull - len(results)
                
    print(("retrieved {count} results across {dbcount} databases").format(count = len(results), dbcount= dbcount))      
    random.shuffle(results)
    
    if(file_type == "csv"):
        res = pd.DataFrame(results)
        return res.to_csv(encoding='utf-8', index=False, columns=['SMILES','zincid','tranche'])
    elif(file_type == "txt"):
        res = pd.DataFrame(results)
        return res.to_csv(encoding='utf-8', index=False, sep="\t", columns=['SMILES','zincid','tranche'])
        
    return results
            
subsets = {
    "lead-like": [(17, 25), 350]
}

def getDistribution(subset=None):
    db.choose_tenant("tin")
    config_conn = psycopg2.connect(Config.SQLALCHEMY_BINDS["zinc22_common"])
    config_curs = config_conn.cursor()
    config_curs.execute("select tranche, host, port from tranche_mappings")
    tranche_map = {}
    db_map = {}
    
    for result in config_curs.fetchall():
        tranche = result[0]
        
        if subset:
            h = int(tranche[1:3])
            p = int(tranche[4:])
            if h >= subsets[subset][0][0] and h <= subsets[subset][0][1] and p <= subsets[subset][1]:
                host = result[1]
                port = result[2]
                db_ = get_conn_string(':'.join([host, str(port)]))
                
                if not db_map.get(db_):
                    db_map[db_] = [tranche]
                else:
                    db_map[db_].append(tranche)
        else:
            host = result[1]
            port = result[2]
            db_ = get_conn_string(':'.join([host, str(port)]))
            
            if not db_map.get(db_):
                db_map[db_] = [tranche]
            else:
                db_map[db_].append(tranche)
    
    tranches = TrancheModel.query.filter_by(charge='-').all()
    size_map = {}
    for i in tranches:
        size_map[i.h_num + i.p_num] = i.sum
    
    db_size_map = {}
    for db_ in db_map.keys():

        db_size_map[db_] = sum([size_map.get(tranche) or 0 for tranche in db_map[db_]])

    total_size = sum(db_size_map.values())

    population = list(db_map.keys())
    distribution = [db_size_map[db_]/total_size for db_ in population]
    
    return population, distribution