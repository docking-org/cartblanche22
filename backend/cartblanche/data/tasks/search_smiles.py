import subprocess
import re
import os
import requests
import tempfile
import time
import json
from celery import current_task, group
from celery.result import AsyncResult, allow_join_result
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
def sw_search(smilelist, dist, adist, zinc22, zinc20, task_id, file_type=None):   
      
    current_task.update_state(task_id=task_id, state='PROGRESS',meta={'current':0, 'projected':100, 'time_elapsed':0})
   
    result = []
    smilelist = smilelist.split('\n')
    processes = []
    print(zinc20)
    print(zinc22)

    # sample url "https://sw.docking.org/search/view?smi=c1ccccc1&smi=Clc1ccccc1&db=zinc22-All-070123.smi.anon&fmt=json"
    results = {}
    import urllib.parse
    search_jobs = []
    
    if zinc22:
        for smile in smilelist:
            search_jobs.append(call_api.s(smile, dist, adist, 'zinc22-All-070123.smi.anon', smile))

    if zinc20:
        for smile in smilelist:
            search_jobs.append(call_api.s(smile, dist, adist, 'all-zinc.smi.anon', matched_smiles=smile))        

    res = group(search_jobs)()
    with allow_join_result():
        while not res.ready():
            count = res.completed_count()
            current_task.update_state(task_id=task_id, state='PREPROCESS',meta={'current':count, 'projected':len(smilelist), 'time_elapsed':0})
            time.sleep(1)
        res = res.get()
        for r in res:
            matched_smiles = r[1]
            r = r[0]
            text = r.split('\n')
            text = text[1:]
            for line in text:
                if line:
                    line = line.split('\t')
                    results[line[0].split(' ')[1]] = {
                        'smiles': line[0].split(' ')[0],
                        'matched_smiles': matched_smiles,
                    }


    # for response in responses:
    #     response = response.json()
    #     print(response)
        # for result in response['results']:
        #     results[result['smiles']] = {
        #         'smiles': result['smiles'],
        #         'matched_smiles': result['matched_smiles'],
        #     }
        
    # url += "db=zinc22-All-070123.smi.anon&fmt=tsv&length=1000&dist={adist}&sdist={dist}".format(adist=adist, dist=dist)
    #     credentials = ('gpcr', 'xtal')

    #     r = requests.get(url, auth=credentials)
    #     print(r)
    #     print(r.text)
    #     text = r.text.split('\n')
    #     text = text[1:]
    
    #     for line in text:
    #         if line:
    #             line = line.split('\t')
    #             results[line[0].split(' ')[1]] = {
    #                 'smiles': line[0].split(' ')[0],
    #                 'matched_smiles': line[1],
    #             }

    # if zinc20:
    #     url = "https://sw.docking.org/search/view?"
    #     for smile in smilelist:
    #         url += "smi={smile}&".format(smile=smile)
    #     url += "db=all-zinc.smi.anon&fmt=tsv&dist={adist}&length=1000&sdist={dist}".format(adist=adist, dist=dist)
    #     credentials = ('gpcr', 'xtal')

    #     r = requests.get(url, auth=credentials)
    #     print(r)
    #     print(r.text)
    #     text = r.text.split('\n')
    #     text = text[1:]

    #     for line in text:
    #         if line:
    #             line = line.split('\t')
    #             results[line[0].split(' ')[1]] = {
    #                 'smiles': line[0].split(' ')[0],
    #                 'matched_smiles': line[1],
    #             }


    # for smile in smilelist:   


        # if zinc22:  
        #     processes.append([smile, subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
        #             "sim -db "+ Config.SMALLWORLD_MAP_PATH + "/zinc22-All.smi.anon.map -v   " \
        #             #grep from =[0-{dist}]
        #             "-n0 -d{adist} -score AtomAlignment '{smiles}' | grep -E '=[0-{dist}] '".format(smiles=smile, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)])



        # if zinc20:
        #     processes.append([smile, subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
        #             "sim -db "+ Config.SMALLWORLD_PUBLIC_MAP_PATH + "/for-sale.smi.anon.map -v   " \
        #             #grep from =[0-{dist}]
        #             "-n0 -d{adist} -score AtomAlignment '{smiles}' | grep -E '=[0-{dist}] '".format(smiles=smile, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)])

    # done = 0
    # for process in processes:
    #     smile = process[0]

    #     out, err = process[1].communicate()
   
    #     for line in out.decode().split('\n'):
    #         if 'ZINC' in line:
    #             result.append(line + ' ' + smile)
    #     done +=1 
    #     current_task.update_state(task_id=task_id, state='PROGRESS',meta={'current':len(processes)/done, 'projected':len(processes), 'time_elapsed':0})
    # hits = {}
    # for line in result:
    #     row = line.split(' ')
        
    #     hits[row[4]] = row[5]
    
    return results

@celery.task
def call_api(smile, dist, adist, db, matched_smiles):
    credentials = ('gpcr', 'xtal')
    import urllib.parse
    smile_text = urllib.parse.quote(smile)
    url = "https://swp.docking.org/search/view?smi={smile}&db={db}&fmt=tsv&dist={adist}&sdist={dist}".format(smile=smile_text, db=db, adist=adist, dist=dist)
    r = requests.get(url, auth=credentials)
    return [r.text, matched_smiles]