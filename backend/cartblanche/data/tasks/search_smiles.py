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
    zinc22, zinc20, discarded = filter_zinc_ids(ids)
    print(zinc20)
    task = [
        getSubstanceList.s(zinc22, role, discarded), zinc20search.s(zinc20)
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
 
    for smile in smilelist:   
        if zinc22:  
            processes.append(subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                    "sim -db "+ Config.SMALLWORLD_MAP_PATH + "/zinc22-All.smi.anon.map -v   " \
                    #grep from =[0-{dist}]
                    "-n0 -d{adist} -score AtomAlignment '{smiles}' | grep -E '=[0-{dist}] '".format(smiles=smile, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE))
        if zinc20:
            processes.append(subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                    "sim -db "+ Config.SMALLWORLD_PUBLIC_MAP_PATH + "/for-sale.smi.anon.map -v   " \
                    #grep from =[0-{dist}]
                    "-n0 -d{adist} -score AtomAlignment '{smiles}' | grep -E '=[0-{dist}] '".format(smiles=smile, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE))

         
    for process in processes:
        out, err = process.communicate()
        result.extend(out.decode().split('\n'))
       
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
