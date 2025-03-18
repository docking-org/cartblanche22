import subprocess
import re
import os
import requests
import tempfile
import time
import json
from celery import current_task, group
from celery.result import AsyncResult, allow_join_result
import pysmallworld
import sys
from cartblanche import celery
from cartblanche.data.tasks.search_zinc import getSubstanceList, zinc20search, mergeResults
from config import Config
from cartblanche.helpers.common import find_molecule, getRole
from cartblanche.helpers.validation import is_zinc22, filter_zinc_ids
from cartblanche.data.tasks import start_search_task
from cartblanche.data.tasks.search_zinc import zinc20search

@celery.task
def filter_sw_results(ids, role, task_id_progress):
    matched_smiles = ids
    print(ids)
    ids = list(ids.keys())

    zinc22, zinc20, discarded = filter_zinc_ids(ids)
    
    task = [
        getSubstanceList.s(zinc22, role, discarded, True, matched_smiles), zinc20search.s(zinc20, matched_smiles)
    ] 

    task = start_search_task.s(task, ids, mergeResults.s(), task_id_progress=task_id_progress)
    task = task.apply_async()
    with allow_join_result():
        res = task.get()['id']

        res = AsyncResult(res).get()
    
        return res

@celery.task
def sw_search(smilelist, dist, adist, zinc22, zinc20, task_id, file_type=None,):
      
    current_task.update_state(task_id=task_id, state='PROGRESS',meta={'current':0, 'projected':100, 'time_elapsed':0})
   
    smilelist = smilelist.split('\n')
    
    # sample url "https://sw.docking.org/search/view?smi=c1ccccc1&smi=Clc1ccccc1&db=zinc22-All-070123.smi.anon&fmt=json"
    results = {}

    search_jobs = []
    
    if zinc22:
        for smile in smilelist:
            swdir = os.environ.get('SWDIR')
            search_jobs.append([smile, dist, adist, 'zinc22-All-070123.smi.anon.map', swdir])
        
    if zinc20:
        for smile in smilelist:
            swdir = os.environ.get('SWDIR_20')
            search_jobs.append([smile, dist, adist, 'all-zinc.smi.anon.map', swdir])

    i = 0

    for job in search_jobs:
        smiles = job[0]
        dist = job[1]
        adist = job[2]
        swdb = job[3]
        swdir = job[4]
        
        db = pysmallworld.Db()
        if not db.set_swdir(swdir):
            print("Warning: SWDIR probably not correct:", swdir, file=sys.stderr)
        if not db.open_map_file(swdb):
            print("Failed to open database file")
            continue
       
        qry = db.new_query()
        qry.add_smiles(smiles)        
        qry.set_max_dist(dist)
        
        scorer = pysmallworld.AtomTypeScoreFunc(qry)
        score = pysmallworld.AlignedScore()
        
        for hit in db.search_query(qry):
            if not scorer.score(score, hit):
                continue
            if score.dist > dist:
                continue
            
            adis = score.fmt(hit.vector).split('=')[1]
            if float(adis) > adist:
                continue

            id = hit.smiles.split(' ')[1]
            results[id] = smiles
        i += 1
        current_task.update_state(task_id=task_id, state='PROGRESS',meta={'current':i, 'projected':len(smilelist), 'time_elapsed':0})
    
    return results