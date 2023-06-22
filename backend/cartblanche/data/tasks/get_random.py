from config import Config
import random
from cartblanche import celery
from cartblanche.helpers.validation import base62, get_conn_string
import time
from cartblanche.data.models.tranche import TrancheModel
import psycopg2


@celery.task
def getRandom(subset, count,timeout=10):
    logp_range="M500 M400 M300 M200 M100 M000 P000 P010 P020 P030 P040 P050 P060 P070 P080 P090 P100 P110 P120 P130 P140 P150 P160 P170 P180 P190 P200 P210 P220 P230 P240 P250 P260 P270 P280 P290 P300 P310 P320 P330 P340 P350 P360 P370 P380 P390 P400 P410 P420 P430 P440 P450 P460 P470 P480 P490 P500 P600 P700 P800 P900".split(" ")
    logp_range={e:i for i, e in enumerate(logp_range)}
    
    total = 0
    result = []
    to_pull = int(count)
    dbcount = 0
    
    population, distribution = getDistribution(subset)    
    results = []     
    tasks = []  
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
                conn = psycopg2.connect(url, connect_timeout=timeout)
                curs = conn.cursor()
                curs.execute('select max(sub_id) from substance;')
                max = curs.fetchone()[0]
                
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
                molecule['SMILES'] = i[1].encode('ascii').replace(b'\x01', b'\\1').decode()
                

                if len(results) < int(count):
                    results.append(molecule)
                
        to_pull = to_pull - len(results)
                
    # print(("retrieved {count} results across {dbcount} databases").format(count = len(results), dbcount= dbcount))      
    random.shuffle(results)

    return results
            
subsets = {
    "lead-like": [(17, 25), 350]
}

def getDistribution(subset=None):
    config_conn = psycopg2.connect(Config.SQLALCHEMY_BINDS["zinc22_common"])
    config_curs = config_conn.cursor()
    config_curs.execute("select tranche, host, port from tranche_mappings")
    tranche_map = {}
    db_map = {}
    
    for result in config_curs.fetchall():
        tranche = result[0]
        print(tranche)
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