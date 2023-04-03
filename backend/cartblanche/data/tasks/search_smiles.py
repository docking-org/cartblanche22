import subprocess
import re
import os
import tempfile
from celery import current_task
from cartblanche import celery

from config import Config

@celery.task
def sw_search(smilelist, dist, adist, file_type=None):     
    current_task.update_state(state='PROGRESS',meta={'current':0, 'projected':100, 'time_elapsed':0})
    result = []
    with tempfile.NamedTemporaryFile() as tmp:
        print(smilelist)
        tmp.write(smilelist.encode())
        tmp.flush()
        res = subprocess.Popen("SWDIR="+ Config.SWDIR + " java -jar " + Config.SMALLWORLD_JAR_PATH + "/sw.jar " \
                            "sim -db "+ Config.SMALLWORLD_MAP_PATH + "/zinc22-All.smi.anon.map -v -n 50000 -d {adist}" \
                            " -score AtomAlignment:SMILES {smiles} | grep '=[0-{dist}] ' ".format(smiles=tmp.name, adist=adist, dist=dist), shell=True, stdout=subprocess.PIPE)
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
