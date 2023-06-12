import subprocess
import re
import os
import tempfile
from celery import current_task
from celery.result import AsyncResult
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
    
    task = [
        getSubstanceList.s(zinc22, role, discarded), zinc20search.s(zinc20)
    ] 

    task = start_search_task.s(task, ids, mergeResults.s(), task_id_progress=task_id_progress)
    task = task.apply_async()
    
    res = task.get()['id']
  
    res = AsyncResult(res).get()
    return res

@celery.task
def sw_search(smilelist, dist, adist, zinc22, zinc20, task_id, file_type=None):     
    current_task.update_state(task_id=task_id, state='PROGRESS',meta={'current':0, 'projected':100, 'time_elapsed':0})
   
    result = []
    
    if zinc22:
        with tempfile.NamedTemporaryFile() as tmp:
            print(smilelist)
            tmp.write(smilelist.encode())
            tmp.flush()
            
            if adist == '0':
                res = subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                            "sim -db "+ Config.SMALLWORLD_MAP_PATH + "/zinc22-All.smi.anon.map -n50" \
                            " {smiles} | grep -E '=[0-{dist}] '".format(smiles=tmp.name, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE) 
            else:
                res = subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                                "sim -db "+ Config.SMALLWORLD_MAP_PATH + "/zinc22-All.smi.anon.map -v   " \
                                #grep from =[0-{dist}]
                                "-n0 -k 20 -score AtomAlignment:SMILES -d{adist} {smiles} | grep -E '=[0-{dist}] '".format(smiles=tmp.name, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)
                                
            
            out, err = res.communicate()
           
            
            result = out.decode().split('\n')
    
    if zinc20:
        with tempfile.NamedTemporaryFile() as tmp:
        
            tmp.write(smilelist.encode())
            tmp.flush()
            
            if adist == '0':
                res = subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                            "sim -db "+ Config.SMALLWORLD_PUBLIC_MAP_PATH + "/for-sale.smi.anon.map -n50" \
                            " {smiles} | grep -E '=[0-{dist}] '".format(smiles=tmp.name, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE) 
            else:
                res = subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                                "sim -db "+ Config.SMALLWORLD_PUBLIC_MAP_PATH + "/for-sale.smi.anon.map -v   " \
                                #grep from =[0-{dist}]
                                "-n0 -k 20 -score AtomAlignment:SMILES -d{adist} {smiles} | grep -E '=[0-{dist}] '".format(smiles=tmp.name, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)
                                
            
            out, err = res.communicate()
            #on console print, print hi
            
            result.extend(out.decode().split('\n'))
            print(result)

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
