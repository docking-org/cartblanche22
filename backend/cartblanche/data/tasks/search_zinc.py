import io
import hashlib
import subprocess, tempfile, io, hashlib, psycopg2
from urllib.parse import quote
import time

import requests
import re
import json
from flask import jsonify, request, redirect, render_template, make_response
from flask_restful import Resource
from celery import chord, current_task, chain, group

from flask_login import current_user
from cartblanche.data.models.default_prices import DefaultPrices
import pandas as pd 
from cartblanche.formatters.format import formatZincResultCSV
from cartblanche.helpers.validation import get_compound_details, get_tin_partition, get_conn_string, get_sub_id, get_zinc_id, get_tranche, get_conn_string, get_tin_partition, identify_dataset
from config import Config
from cartblanche import celery
from rdkit import Chem
import pprint
from rdkit.Chem import Descriptors

from cartblanche.email_send import send_search_log

client_configuration = {
        "mem_max_sort" : int(5.12e8), # in bytes
        "mem_max_cached_file" : 0
}

from contextlib import contextmanager
#for psycopg2 not allowing copy_from to be used in a transaction
#https://stackoverflow.com/questions/34812942/psycopg2-copy-from-raises-asynchronous-programmingerror-with-sync-connection-in
@contextmanager
def _paused_thread():
    try:
        thread = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        yield
    finally:
        psycopg2.extensions.set_wait_callback(thread)

@celery.task
def mergeResults(res, submission = None):
    for i in res:
        print(i)
    if isinstance(res, list):
        if isinstance(res[0], dict):
            for i in range(1, len(res)):
                
                if res and res[i]:
                    res[0].update(res[i])
            res = res[0]
        else:
            result = []
            for i in res:
                result += i
            res = result

    if submission:
        res['submission'] = submission
    return res

def formatZincID(sub_id):
    #ZINC000000000007
    return 'ZINC' + str(sub_id).zfill(12)
        
@celery.task
def zinc20search(zinc20, matched_smiles=None):

    if len(zinc20) == 0:
        return []
    fixed = []
    for i in zinc20:
        
        if 'ZINC' in str.upper(str(i)):
            i = str.upper(i).split('ZINC')[1]
        elif 'C' in str.upper(i):
            i = str.upper(i).split('C')[1]
        fixed.append(i)
    zinc20 = fixed

    db = psycopg2.connect(Config.SQLALCHEMY_BINDS['zinc20'])
    curs = db.cursor()
    
    curs.execute("select sub_id_fk, supplier_code, catalog.name, catalog.purchasable, smiles from catalog_item\
                  left join catalog on cat_id_fk = cat_id left join substance on sub_id_fk = sub_id where sub_id_fk in %s", (tuple(zinc20),))
    result = {}
    for i in curs.fetchall():

        smiles = i[4]
        mol = Chem.MolFromSmiles(smiles)
        
        if i[0] not in result:

            result[i[0]] = {}
            if matched_smiles and matched_smiles.get(formatZincID(i[0])):
                result[i[0]]['matched_smiles'] = matched_smiles[formatZincID(i[0])]
            result[i[0]]['smiles'] = smiles
            result[i[0]]['tranche_details'] = {
                'heavy_atoms': mol.GetNumHeavyAtoms(),
                'logp': round(Descriptors.MolLogP(mol),3),
                'mwt': round(Descriptors.MolWt(mol),3),
                'inchi': Chem.MolToInchi(mol),
                'inchikey': Chem.MolToInchiKey(mol),
            }
            result[i[0]]['mol_formula'] = Chem.rdMolDescriptors.CalcMolFormula(mol)
            result[i[0]]['rings'] = Chem.rdMolDescriptors.CalcNumRings(mol)
            result[i[0]]['hetero_atoms'] = Chem.rdMolDescriptors.CalcNumHeteroatoms(mol)

            result[i[0]]['db'] = 'zinc20'
            result[i[0]]['zinc_id'] = formatZincID(i[0])
            result[i[0]]['catalogs'] = []
        result[i[0]]['catalogs'].append({
            'catalog_name': i[2],
            'price': 240,
            'purchase': 1,
            'quantity': 10,
            'shipping': "6 weeks",
            'supplier_code': i[1],
            'unit': "mg"
            })
        
    results = []
    for i in result:
        results.append(result[i])

        
    return {'zinc20':results}
   
@celery.task
def vendorSearch(vendor_ids, role='public'):
    result = {}
    t_start = time.time()
    logs = []
    current_task.update_state(state='PROGRESS',meta={'current':0, 'projected':100, 'time_elapsed':0})
    # all configuration prepartion
    config_conn = psycopg2.connect(Config.SQLALCHEMY_BINDS['zinc22_common'])
    config_curs = config_conn.cursor()
    config_curs.execute("select tranche, host, port from tranche_mappings")
    tranche_map = {}
    for result in config_curs.fetchall():
        tranche = result[0]
        host = result[1]
        port = result[2]
        tranche_map[tranche] = ':'.join([host, str(port)])
    config_curs.execute("select machine_id, hostname, port from tin_machines")
    # extra configuration for cartblanche, translates machine_id to host:port
    machine_id_map = {}
    for result in config_curs.fetchall():
        machine_id = result[0]
        host = result[1]
        port = result[2]
        machine_id_map[machine_id] = ':'.join([host, str(port)])
  
    sb_partition_map = {}
    config_curs.execute("select hashseq, host, port from antimony_hash_partitions ahp left join antimony_machines am on ahp.partition = am.partition")
    for result in config_curs.fetchall():
        hashseq = result[0]
        host    = result[1]
        port    = result[2]
        sb_partition_map[hashseq] = ':'.join([host, str(port)])
  
    input_size = len(vendor_ids)
    
    expected_result_size = input_size * 2.5
    if expected_result_size > client_configuration["mem_max_cached_file"]:
        data_file = tempfile.NamedTemporaryFile(mode='w+')
        tf_input  = tempfile.NamedTemporaryFile(mode='w+')
        tf_inter  = tempfile.NamedTemporaryFile(mode='w+')
    else:
        # use stringIO if the file is small enough to fit into memory
        data_file = io.StringIO()
        tf_input  = tempfile.NamedTemporaryFile(mode='w+', dir='/dev/shm') # to use gnu sort we need an actual file (or a thread writing the StringIO data concurrently, which is too complicated for my taste)
        tf_inter  = tempfile.NamedTemporaryFile(mode='w+', dir='/dev/shm')
        
    with data_file, tf_input, tf_inter, tempfile.NamedTemporaryFile(mode='w+') as output_file, tempfile.NamedTemporaryFile(mode='w+') as missing_file:
        result = {}
        def sha256(a):
            return hashlib.sha256(a.encode('utf-8')).hexdigest()
        total_length = 0
 
        for vendor in vendor_ids:
            vendor = vendor.strip()
            v_partition = sha256(vendor)[-4:-2] # leftmost two digits of rightmost four digits makes up the database key
            v_db = sb_partition_map[v_partition]
            tf_input.write("{} {}\n".format(vendor, v_db))
            total_length += 1
        tf_input.flush()
    
        # ========== FIRST SORT PROC- SEARCH SB ==========
        # limit sort memory usage according to configuration, we want the client-side search process to have as low a footprint as possible, while remaining fast for typical usage
        sort_mem_arg = "{}K".format(client_configuration["mem_max_sort"]//1000)
        
        # sort by the database each id belongs to 
        with subprocess.Popen(["/usr/bin/sort", "-k2", "-S{}".format(sort_mem_arg), tf_input.name], stdout=subprocess.PIPE) as sort_proc:
            def search(p_id, data_file, output_file, missing_file):
                search_conn = None
                try:
                    data_file.flush()
                    data_file.seek(0)
                    search_database = get_conn_string(p_id, user='antimonyuser', db='antimony')
                    logs.append("searching "+ search_database)
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    # output fmt: VENDOR CAT_CONTENT_ID MACHINE_ID
                    get_vendor_results_antimony(data_file, search_curs, output_file, missing_file)
                except psycopg2.OperationalError as e:
                    message = "failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database)
               
                    logs.append(message)
                    for line in data_file:
                        vendor = line.strip()
                        missing_file.write(vendor +'\n')
                finally:
                    if search_conn: search_conn.close()
        
            p_id_prev = None
            projected_size = 0
            curr_size = 0
            for line in sort_proc.stdout:
                vendor, p_id = line.decode('utf-8').strip().split()
                if p_id != p_id_prev and p_id_prev != None:
                    t_elapsed = time.time() - t_start
                    current_task.update_state(state='PROGRESS',meta={'current':curr_size, 'projected':projected_size, 'time_elapsed':t_elapsed})
                    
                    search(p_id_prev, data_file, tf_inter, missing_file) # set our "missing" file as output
                    curr_size += projected_size
                    projected_size = 0
                    data_file.seek(0)
                    data_file.truncate()
                data_file.write(vendor + '\n')
                projected_size += 1
                p_id_prev = p_id
            if projected_size > 0:
                t_elapsed = time.time() - t_start
                current_task.update_state(state='PROGRESS',meta={'current':curr_size, 'projected':projected_size, 'time_elapsed':t_elapsed})
        
                search(p_id_prev, data_file, tf_inter, missing_file)
                data_file.seek(0)
                data_file.truncate()
                
        t_elapsed = time.time() - t_start
        current_task.update_state(state='PROGRESS',meta={'current':total_length, 'projected':projected_size, 'time_elapsed':t_elapsed})
        #printProgressBar(total_length, total_length, prefix = "", suffix="done searching sb!", length=50, t_elapsed=t_elapsed)
        tf_inter.flush()
        
        missing_file.seek(0)
        
      
                
        # ========== SECOND SORT PROC- SEARCH SN =============
        with subprocess.Popen(["/usr/bin/sort", "-k3", "-S{}".format(sort_mem_arg), tf_inter.name], stdout=subprocess.PIPE) as sort_proc:
            def search(p_id, data_file, output_file):
                search_conn = None
                try:
                    data_file.flush()
                    data_file.seek(0)
                    search_database = get_conn_string(p_id)
                    logs.append("searching "+ search_database)
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    t_elapsed = time.time() - t_start
                    get_vendor_results_cat_id(data_file, search_curs, output_file)
                except psycopg2.OperationalError as e:
                    message = "failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database)
                    print(message)
                    logs.append(message)
                    # for line in data_file:
                    #     print(line)
                    #     vendor = line
                    #     tokens = ["_null_", "_null_", "_null_", str(line), "_null_"]
                    #     output_file.write('\t'.join(tokens) +'\n')
                finally:
                    if search_conn: search_conn.close()
                    
            p_id_prev = None
            projected_size = 0
            curr_size = 0
            for line in sort_proc.stdout:
                vendor, cat_content_id, p_id = line.decode('utf-8').strip().split()
                if p_id != p_id_prev and p_id_prev != None:
                    t_elapsed = time.time() - t_start
                    p_id_prev = machine_id_map[int(p_id_prev)] # correct from number to actual database
                    current_task.update_state(state='PROGRESS',meta={'current':curr_size, 'projected':total_length, 'time_elapsed':t_elapsed})
                    search(p_id_prev, data_file, output_file)
                    data_file.seek(0)
                    data_file.truncate()
                    curr_size += projected_size
                    projected_size = 0
                data_file.write(vendor + '\n')
                projected_size += 1
                p_id_prev = p_id
            if projected_size > 0:
                p_id_prev = machine_id_map[int(p_id_prev)]
                current_task.update_state(state='PROGRESS',meta={'current':curr_size, 'projected':total_length, 'time_elapsed':t_elapsed})
                search(p_id_prev, data_file, output_file)
    
        t_elapsed = time.time() - t_start
        current_task.update_state(state='PROGRESS',meta={'current':total_length, 'projected':total_length, 'time_elapsed':t_elapsed})
        
        output_file.seek(0)
        
        result = []
        for line in output_file.readlines():
            for line in json.loads(line):
                result.append(line)

        getPrices(result, role)

        return {'zinc22':result, 'zinc22_missing': missing_file.read().split("\n"), 'logs': logs}
    
    
@celery.task
def getSubstanceList(zinc_ids, role='public', discarded = None, get_vendors=True, matched_smiles=None):
    
    t_start = time.time()
    logs = []
    current_task.update_state(state='PROGRESS',meta={'current':0, 'projected':100, 'time_elapsed':0})
    # all configuration prepartion
    config_conn = psycopg2.connect(Config.SQLALCHEMY_BINDS["zinc22_common"])
    config_curs = config_conn.cursor()
    config_curs.execute("select tranche, host, port from tranche_mappings")
    tranche_map = {}
    for result in config_curs.fetchall():
        tranche = result[0]
        host = result[1]
        port = result[2]
        tranche_map[tranche] = ':'.join([host, str(port)])

    input_size = len(zinc_ids)
    expected_result_size = (input_size*8) if get_vendors else (input_size*4)
    if expected_result_size > client_configuration["mem_max_cached_file"]:
        data_file = tempfile.NamedTemporaryFile(mode='w+')
        tf_input  = tempfile.NamedTemporaryFile(mode='w+')
    else:
        # use stringIO if the file is small enough to fit into memory
        data_file = io.StringIO()
        tf_input  = tempfile.NamedTemporaryFile(mode='w+') # except for this, see explanation in similar section above

    with tf_input, tempfile.NamedTemporaryFile(mode='w+') as output_file, data_file, tempfile.NamedTemporaryFile(mode='w+') as missing_file:
        result = {}
        total_length = 0
        
        for zinc_id in zinc_ids:
            zinc_id = zinc_id.strip()
            id_partition = get_tin_partition(zinc_id, tranche_map)
            if id_partition != 'fake':
                tf_input.write("{} {}\n".format(zinc_id, id_partition))
                total_length += 1
            else:
                missing_file.write(zinc_id + "\n")    
        tf_input.flush()
        missing_file.flush()
        # limit sort memory usage according to configuration, we want the client-side search process to have as low a footprint as possible, while remaining fast for typical usage
        sort_mem_arg = "{}K".format(client_configuration["mem_max_sort"]//1000)
        
        # sort by the database each id belongs to 
        with subprocess.Popen(["/usr/bin/sort", "-k2", "-S{}".format(sort_mem_arg), tf_input.name],  stdout=subprocess.PIPE) as sort_proc:        
            def search(p_id, data_file, output_file, tranches_internal):
                search_conn = None
                try:
                    data_file.flush()
                    data_file.seek(0)
                  
                    search_database = get_conn_string(p_id)
                    logs.append("searching "+ search_database)
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    t_elapsed = time.time() - t_start
                    if get_vendors:
                        get_vendor_results(data_file, search_curs, output_file, tranches_internal)
                    else:
                        get_smiles_results(data_file, search_curs, output_file, tranches_internal)
                        
                except psycopg2.OperationalError as e:
                    message = "failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database)
                    print(message)
                    logs.append(message)
                    tranches_internal_rev = {t[1] : t[0] for t in tranches_internal.items()}
                    for line in data_file:
                        sub_id, tranche_id_int = line.split()
                        sub_id = int(sub_id)
                        tranche = tranches_internal_rev[int(tranche_id_int)]
                        tokens = get_zinc_id(sub_id, tranche)
                        missing_file.write(tokens +'\n')
                except :
                    message = "An error occurred while searching {}.".format(search_database)
                    print(message)
                    logs.append(message)
                    tranches_internal_rev = {t[1] : t[0] for t in tranches_internal.items()}
                    for line in data_file:
                        sub_id, tranche_id_int = line.split()
                        sub_id = int(sub_id)
                        tranche = tranches_internal_rev[int(tranche_id_int)]
                        tokens = get_zinc_id(sub_id, tranche)
                        missing_file.write(tokens +'\n')
                finally:
                    if search_conn: search_conn.close()
            
            p_id_prev = None
            projected_size = 0
            curr_size = 0
            tranches_internal = {}
            for line in sort_proc.stdout:
                zinc_id, p_id = line.decode('utf-8').strip().split()
                if p_id != p_id_prev and p_id_prev != None:
                    t_elapsed = time.time() - t_start
                    current_task.update_state(state='PROGRESS',meta={'current':curr_size, 'projected':total_length, 'time_elapsed':t_elapsed})
                
                    search(p_id_prev, data_file, output_file, tranches_internal)
                
                    curr_size += projected_size
                    projected_size = 0
                    tranches_internal.clear()
                    data_file.seek(0)
                    data_file.truncate()
                sub_id, tranche = get_sub_id(zinc_id), get_tranche(zinc_id)
                tranche_id_int = tranches_internal.get(tranche)

                # instead of copying the tranche configuration over from the backend server, we just create our own here
                # we don't use tranche information from zinc22, we keep the tranche information encoded in the input zinc id. 
                # zinc22 tranches have occasionally mutated one or two off and we want to avoid user confusion (what is this new zinc id doing in my output ?!)
                if not tranche_id_int:
                    # the whole point of this is to reduce the overhead of carrying the original tranche information through the query, so reduce it to smallint size (char(2)) instead of char(8)
                    tranche_id_int = len(tranches_internal)+1
                    assert(tranche_id_int < 65536) # keep size under postgres smallint limit
                    tranches_internal[tranche] = tranche_id_int

                data_file.write(str(sub_id) + '\t' + str(tranche_id_int) + '\n')
                projected_size += 1
                p_id_prev = p_id
            if projected_size > 0:
                t_elapsed = time.time() - t_start
                current_task.update_state(state='PROGRESS',meta={'current':curr_size, 'projected':total_length, 'time_elapsed':t_elapsed})
                #printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)

                search(p_id_prev, data_file, output_file, tranches_internal)
                
        t_elapsed = time.time() - t_start
        output_file.seek(0)
        result = []
        for line in output_file.readlines():
            try:
                for line in json.loads(line):
                    if line.get('zinc_id') and matched_smiles:
                        line['matched_smiles'] = matched_smiles[line['zinc_id']]                        
                    print(line)
                    result.append(line)

            except:
                continue

        missing_file.seek(0)

        current_task.update_state(state='PROGRESS',meta={'current':total_length, 'projected':total_length, 'time_elapsed':t_elapsed})

        getPrices(result, role)
      
        return {'zinc22':result, 'zinc22_missing':missing_file.read().split("\n"), 'logs':logs}
        



def get_smiles_results(data_file, search_curs, output_file, tranches_internal):
    search_curs.execute("create temporary table cb_sub_id_input (sub_id bigint, tranche_id_orig smallint)")
    with _paused_thread():
        search_curs.copy_from(data_file, 'cb_sub_id_input', sep='\t', columns=['sub_id', 'tranche_id_orig'])
    search_curs.execute("create temporary table cb_sub_output (smiles text, sub_id bigint, tranche_id smallint, tranche_id_orig smallint)")
    search_curs.execute("call get_some_substances_by_id('cb_sub_id_input', 'cb_sub_output')")
    search_curs.execute("select smiles, sub_id, tranche_id_orig from cb_sub_output")

    parse_tin_results(search_curs, output_file, tranches_internal, True)

def get_vendor_results(data_file, search_curs, output_file, tranches_internal):
    search_curs.execute("create temporary table cb_sub_id_input (sub_id bigint, tranche_id_orig smallint)")
    with _paused_thread():
        search_curs.copy_from(data_file, 'cb_sub_id_input', sep='\t', columns=['sub_id', 'tranche_id_orig'])
    search_curs.execute("create temporary table cb_pairs_output (smiles text, sub_id bigint, tranche_id smallint, supplier_code text, cat_content_id bigint, cat_id_fk smallint, tranche_id_orig smallint)")
    search_curs.execute("call cb_get_some_pairs_by_sub_id()")
    search_curs.execute("select smiles, sub_id, tranche_id_orig, supplier_code, catalog.short_name from cb_pairs_output left join catalog on cb_pairs_output.cat_id_fk = catalog.cat_id")
    
    parse_tin_results(search_curs, output_file, tranches_internal)
    
def get_vendor_results_antimony(data_file, search_curs, output_file, missing_file):
    search_curs.execute("create temporary table tq_in (supplier_code text)")
    with _paused_thread():
        search_curs.copy_from(data_file, 'tq_in', columns=['supplier_code'])
    # we have a more standard query for antimony, since it's not as complicated as tin and therefore doesn't need custom database functions
    search_curs.execute("select tq_in.supplier_code, cat_content_id, machine_id_fk from tq_in left join supplier_codes on tq_in.supplier_code = supplier_codes.supplier_code left join supplier_map on sup_id = sup_id_fk")
    
    results = search_curs.fetchmany(5000)
    while len(results) > 0:
        for result in results:
            supplier_code   = result[0]
            cat_content_id  = result[1]
            machine_id_fk   = result[2]
            if not cat_content_id:
                # we need to pass data returned by antimony to tin
                # it doesn't make sense to look up a bunch of nulls, so save the misses from this stage separately and add them to the end result later
                missing_file.write(supplier_code + '\n')
            else:
                output_file.write('\t'.join([supplier_code, str(cat_content_id), str(machine_id_fk)]) + '\n')
        results = search_curs.fetchmany(5000)

def get_vendor_results_cat_id(data_file, search_curs, output_file):
    search_curs.execute("create temporary table cb_vendor_input (supplier_code text)")
    with _paused_thread():
        search_curs.copy_from(data_file, 'cb_vendor_input', sep=',', columns=['supplier_code'])
    search_curs.execute("create temporary table cb_pairs_output (smiles text, sub_id bigint, tranche_id smallint, supplier_code text, cat_content_id bigint, cat_id smallint)")
    search_curs.execute("call cb_get_some_pairs_by_vendor()")
    search_curs.execute("select smiles, sub_id, tranches.tranche_name, supplier_code, catalog.short_name from cb_pairs_output left join tranches on cb_pairs_output.tranche_id = tranches.tranche_id left join catalog on cb_pairs_output.cat_id = catalog.cat_id")
    
    parse_tin_results(search_curs, output_file)

def parse_tin_results(search_curs, output_file, tranches_internal= None, smiles_only=False):
    output = []
    ids = {}

    if tranches_internal:
        tranches_internal_rev = { t[1] : t[0] for t in tranches_internal.items() }
        
    results = search_curs.fetchmany(5000)

    while len(results) > 0:
        for result in results:
            if result[0]:  
                smiles          = result[0].encode('ascii').replace(b'\x01', b'\\1').decode()
                sub_id          = result[1]
                if tranches_internal:
                    tranche_id_orig = result[2]
                    tranche_name    = tranches_internal_rev[tranche_id_orig]
                else:
                    tranche_name = result[2]
                zinc_id = get_zinc_id(sub_id, tranche_name)
                if not smiles_only:
                    supplier_codes   = result[3]
                    catalog        = result[4]
                    tranche_details = get_compound_details(smiles)
                    mol = Chem.MolFromSmiles(smiles)
                    if not zinc_id in ids:
                        ids[zinc_id] = {
                        "zinc_id":zinc_id, 
                        "sub_id":sub_id, 
                        "smiles":smiles, 
                        "tranche":{
                            "h_num": tranche_name[0:3],
                            "logp": zinc_id[5:6],
                            "mwt": zinc_id[4:5],
                            "p_num": tranche_name[3:]
                        },         
                        "catalogs": [{"catalog_name": catalog, "supplier_code": supplier_codes}] if catalog else [], 
                        "tranche_details": tranche_details,
                        "mol_formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
                        "rings": Chem.rdMolDescriptors.CalcNumRings(mol),
                        "hetero_atoms": Chem.rdMolDescriptors.CalcNumHeteroatoms(mol),
                        }
                    else:
                        if catalog:
                            ids[zinc_id]["catalogs"].append({
                                "catalog_name": catalog,
                                "supplier_code": supplier_codes
                            })
                            
                else:
                    ids[zinc_id] = {
                        "zinc_id":zinc_id, 
                        "smiles":smiles
                    }
        results = search_curs.fetchmany(5000)
        
    output = list(ids.values())
    output_file.write(json.dumps(output) + "\n")
    output_file.flush()

def getPrices(result, role):
    for data in result:
            if data.get('catalogs'):
                    catalogs = data['catalogs']
                    mol20 = None
                    # for c in catalogs:
                    #     if 'zinc' in c['supplier_code'].lower():
                    #         mol20 = c['supplier_code']
                    #         catalogs.remove(c)
                    
                    # if mol20:
                    #     prices = zinc20search(mol20)
                    #     if prices:
                    #         if prices.get('catalogs'):
                    #             prices = prices['catalogs']
                    #             for p in prices:
                    #                 catalogs.append(p)
                    for c in catalogs:
                        if c.get('catalog_name'):
                            s = c['catalog_name'].lower()
                            code = c['supplier_code']

                            price = None
                            if identify_dataset(code):
                                price = DefaultPrices.query.filter_by(category_name=identify_dataset(code), organization=role).first()
                            
                            
                            elif 'zinc' in code.lower():
                                print()
                                                    

                            else:
                                price = DefaultPrices.query.filter_by(short_name=s, organization=role).first()

                            

                            if price:
                                c['short_name'] = c['catalog_name']
                                c['catalog_name'] = price.category_name
                                c['quantity'] = price.quantity
                                c['unit'] = price.unit
                                c['shipping'] = price.shipping
                                c['price'] = price.price
                        

            smile = data['smiles'].encode('ascii')
            smile = smile.replace(b'\x01', b'\\1')
            smile = smile.decode()
            data['smiles'] = smile
            data['db'] = 'zinc22'