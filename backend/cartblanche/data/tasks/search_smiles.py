import subprocess
import re
import os
import tempfile
from celery import current_task
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
    ids = ids.keys()

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
    for smile in smilelist:   
        if zinc22:  
            processes.append([smile, subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                    "sim -db "+ Config.SMALLWORLD_MAP_PATH + "/zinc22-All.smi.anon.map -v   " \
                    #grep from =[0-{dist}]
                    "-n0 -d{adist} -score AtomAlignment '{smiles}' | grep -E '=[0-{dist}] '".format(smiles=smile, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)])

                
                
        if zinc20:
            processes.append([smile, subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                    "sim -db "+ Config.SMALLWORLD_PUBLIC_MAP_PATH + "/for-sale.smi.anon.map -v   " \
                    #grep from =[0-{dist}]
                    "-n0 -d{adist} -score AtomAlignment '{smiles}' | grep -E '=[0-{dist}] '".format(smiles=smile, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)])

         
    for process in processes:
        smile = process[0]

        out, err = process[1].communicate()
        
        for line in out.decode().split('\n'):
            if 'ZINC' in line:
                result.append(line + ' ' + smile)

    hits = {}
    for line in result:
        row = line.split(' ')
        
        hits[row[4]] = row[5]
    print(hits)
    return hits
