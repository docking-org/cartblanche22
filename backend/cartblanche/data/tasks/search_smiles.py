import subprocess
import re
import os
import requests
import tempfile
import time
import json
from celery import current_task, group
from celery.result import AsyncResult, allow_join_result
from celery_batches import Batches
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
def sw_search(smilelist, dist, adist, zinc22, zinc20, task_id, file_type=None, base=Batches, rate_limit='5/s', flush_every=100, flush_interval=10):
      
    current_task.update_state(task_id=task_id, state='PROGRESS',meta={'current':0, 'projected':100, 'time_elapsed':0})
   
    result = []
    smilelist = smilelist.split('\n')
    processes = []
   

    # sample url "https://sw.docking.org/search/view?smi=c1ccccc1&smi=Clc1ccccc1&db=zinc22-All-070123.smi.anon&fmt=json"
    results = {}

    search_jobs = []
    
    if zinc22:
        for smile in smilelist:
            search_jobs.append([smile, dist, adist, 'zinc22-All-070123.smi.anon', smile])

    if zinc20:
        for smile in smilelist:
            search_jobs.append([smile, dist, adist, 'all-zinc.smi.anon', smile])
    
    i = 0
    for job in search_jobs:
        smile = job[0]
        dist = job[1]
        adist = job[2]
        db = job[3]
        matched_smiles = job[4]
        
        res = call_api(smile, dist, adist, db, matched_smiles)
    
        
        matched_smiles = res[1]
        r = res[0]
        print(r)
        text = r.split('\n')
        text = text[1:]
        for line in text:
            if line:
                line = line.split('\t')
                results[line[0].split(' ')[1]] = {
                    'smiles': line[0].split(' ')[0],
                    'matched_smiles': matched_smiles,
                }
        i += 1
        current_task.update_state(task_id=task_id, state='PROGRESS',meta={'current':i, 'projected':len(smilelist), 'time_elapsed':0})
        time.sleep(5)
    
    print(results)
    
    return results

@celery.task
def call_api(smile, dist, adist, db, matched_smiles):
    credentials = ('gpcr', 'xtal')
    import urllib.parse
    smile_text = urllib.parse.quote(smile)
    url = "https://swp.docking.org/search/view?smi={smile}&db={db}&fmt=tsv&dist={adist}&sdist={dist}&length=25".format(smile=smile_text, db=db, adist=adist, dist=dist)
    
    r = requests.get(url, auth=credentials)
    
    if not r.text.split('\n')[1]:
        url = "https://sw.docking.org/search/view?smi={smile}&db=all-zinc.smi.anon&fmt=tsv&dist={adist}&sdist={dist}&length=25".format(smile=smile_text, db=db, adist=adist, dist=dist)
        r = requests.get(url, auth=credentials)
       
        
    return [r.text, matched_smiles]