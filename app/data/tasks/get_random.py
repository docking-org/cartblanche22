

from app.data.models.tin.substance import SubstanceModel
from config import Config

import app
import random
import string
from app.main import application
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, reqparse
from app.celery_worker import celery, flask_app, db
from celery.execute import send_task
from flask import render_template, request

from app.helpers.validation import base62, get_tranche
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
            ids = []
            count = 0
            while count < 100:
                id = "ZINC"
                id = id + random.choice(string.ascii_lowercase + string.digits) + random.choice(string.ascii_lowercase + string.digits)
                id = id + "00000"
                for i in range(5):
                    id = id + random.choice(string.ascii_letters + string.digits)
                if get_tranche(id) != "fake":
                    ids.append(id)
                    count += 1
                
            print(ids)
            task = send_task('app.data.tasks.search_zinc.getSubstanceList', [[], ids, False]) 
            res = task.get()
            data= res[1]["found"]
            results = data
            
            
            if(file_type == "csv"):
                res = pd.DataFrame(results)
                return res.to_csv(encoding='utf-8', index=False)
            elif(file_type == "txt"):
                res = pd.DataFrame(results)
                return res.to_csv(encoding='utf-8', index=False, sep=" ")
                
            return results
           
        except Exception as e:
            print(e)



#  tstart = time.time()
#     conn = psycopg2.connect(dsn, connect_timeout=timeout)
#     curs = conn.cursor()