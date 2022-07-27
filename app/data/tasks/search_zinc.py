import io
import hashlib
import subprocess, tempfile, io, hashlib, psycopg2
from urllib.parse import quote
import time
import requests
import re
import json
from flask import jsonify, request, redirect, render_template
from flask_restful import Resource
from celery import chord, current_task
from celery.result import AsyncResult

from app.helpers.validation import get_compound_details, get_tin_partition, get_conn_string, get_sub_id, get_zinc_id, get_tranche, get_conn_string, get_tin_partition
from app.main import application
from config import Config
from app.celery_worker import celery, flask_app, db
from app.email_send import send_search_log

client_configuration = {
        "mem_max_sort" : int(5.12e8), # in bytes
        #"mem_max_cached_file" : int(2.56e8), # in bytes
        "mem_max_cached_file" : 0
}

@application.route('/search/progress', methods=['GET'])
def search_status():
    data = request.args.get("task")
    
    task = AsyncResult(data)
    data = task.get()
    data = data[1][1]
  
    total = len(data)
    done = 0
    for task in data:
        res = AsyncResult(str(task))
        if res.ready():
            done +=1
   
    if done != 0:
        if (done/total) == 1:
            return redirect("/search/result?task="+request.args.get("task"), code=200)
        return render_template('search/result_status.html', progress = round((done/total), 2))
    else:
        return render_template('search/result_status.html', progress = 0)
    
@application.route('/search/update_progress', methods=['GET'])
def update_progress():
    data = request.args.get("task")
    
    task = AsyncResult(data)
    data = task.get()
    
   
    total = len(data)
    done = 0
    for task in data:
        res = AsyncResult(task)
        if res.ready():
            done +=1
 
    
    if done != 0:
        if (done/total) == 1:
            return jsonify(1)
        return jsonify(round((done/total),2))
    else:
        return jsonify(0)
    
@application.route('/search/result_zincsearch', methods=['GET'])
def search_result():
    if request.method == 'GET':
        data = request.args.get("task")
        
        task = AsyncResult(data)
        data = task.get()

        list20 = data[0]
        list22 = data[1]["found"]
        missing = data[1]["missing"][:-1]
        
        for entry in list22:
            print(entry["smiles"])
            entry["smiles_url"] = quote(entry["smiles"])
            
        if(len(list22) == 0 and len(list20) == 0):
            return render_template('errors/search404.html', href='/search/search_byzincid', header="We didn't find those molecules in the Zinc22 database. Click here to return"), 404
        return render_template('search/result_zincsearch.html', data22=list22, data20=list20, missing22=missing)

@application.route('/search/result_suppliersearch', methods=['GET'])
def search_result_supplier():
        if request.method == 'GET':
            data = request.args.get("task")
            task = AsyncResult(data)
            list22 = task.get()['found']
            missing = task.get()['missing']
            print(missing)
            for entry in list22:
                print(entry["smiles"])
                entry["smiles_url"] = quote(entry["smiles"])
       
            if len(list22) == 0:
                return render_template('errors/search404.html', href='/search/search_byzincid', header="We didn't find those molecules in the Zinc22 database. Click here to return"), 404
            return render_template('search/result_supplier.html', data22=list22, data20=[], missing22=missing)

class SearchJobSupplier(Resource):
    def post(self):
        data = request.form['supplierTextarea']
        file = request.files['supplierfile'].read().decode("utf-8")
        file = file.split("\n")
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        codes = file + textDataList
        codes = [code for code in codes if code != '']
        print(codes)
    
        try:
            task = vendorSearch.delay(codes)
        except Exception as e:
            print(e)
    
        return redirect('/search/result_suppliersearch?task={}'.format(task))
            
    def curlSearch(data):
        try:
            task = vendorSearch.delay(data)
        except Exception as e:
            print(e)
        return task

class SearchJobSubstance(Resource):
    def post(self):
        data = request.form['myTextarea']
        file = request.files['zincfile'].read().decode()
        file = [x for x in re.split(r'\n|\r|(\r\n)', file) if x!='' and x!= None]
    
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        
        ids = textDataList + file
        
        zinc22, zinc20, discarded = SearchJobSubstance.filter_zinc_ids(ids)
        print(zinc22, zinc20, discarded)
        zinc20 = zinc20search(zinc20)

        try:
            task = chord([search20.s(zinc20=zinc20), getSubstanceList.s(zinc22)])(mergeResults.s())
        except Exception as e:
            print("err", e)
        
        if(len(ids) > 300):
            return redirect('/search/progress?task={task}'.format(task = task.id))
        else:
            return redirect('/search/result_zincsearch?task={task}'.format(task = task.id))

    def filter_zinc_ids(ids):
        zinc22 = []
        zinc20 = []
        discarded = []

        for identifier in ids:
            if '-' in identifier:
                def checkHasZinc(identifier):
                    if identifier[0:4].upper() != 'ZINC':
                        identifier_ = 'ZINC' + identifier
                        return identifier_.replace('-', (16 - len(identifier_) + 1) * '0')
                    
                    return identifier.replace('-', (16 - len(identifier) + 1) * '0')
                new_identifier = checkHasZinc(identifier)
                print(new_identifier, identifier, len(new_identifier))
                zinc22.append(new_identifier)
                continue
            
            if identifier[0:1].upper() == 'C':
                identifier = identifier.replace('C', 'ZINC')
                print(identifier)
                
            if identifier[4:6] == '00':
                zinc20.append(identifier)
                continue

            elif identifier.isnumeric():
                id = 'ZINC' + ((12 - len(identifier)) * '0') + identifier
                zinc20.append(id)
                continue

            elif identifier[0:4].upper() == 'ZINC':
                if(identifier[4:5].isalpha()):
                    zinc22.append(identifier)
                else:
                    id = 'ZINC' + identifier.replace(identifier, (16 - len(identifier) + 1) * '0') + identifier[4:]
                    print(id)
                    zinc20.append(id)
                continue
            else:
                discarded.append(identifier)
        return zinc22, zinc20, discarded

@celery.task
def mergeResults(args):
    return args

def zinc20search(zinc20):
    zinc20_response = None
    data20 = []
    if len(zinc20) > 0:
        zinc20_files = {
            'zinc_id-in': zinc20,
            'output_fields': "zinc_id supplier_code smiles substance_purchasable"
        }
        zinc20_response = requests.post("https://zinc20.docking.org/catitems.txt", data=zinc20_files)

    if zinc20_response:
        zinc20_data = {}
        for line in zinc20_response.text.split('\n'):
            temp = line.split('\t')
            if len(temp) == 4:
                identifier, supplier_code, smiles, purchasibility = temp[0], temp[1], temp[2], temp[3]
                if identifier not in zinc20_data:
                    zinc20_data[identifier] = {
                        'identifier': identifier,
                        'zinc_id': identifier,
                        'smiles': smiles,
                        'catalogs_new': [{'supplier_code': supplier_code, 'purchasibility': purchasibility}],
                        'catalogs': supplier_code,
                        'supplier_code': supplier_code,
                        'db': 'zinc20'
                    }
                else:
                    catalogs = zinc20_data[identifier]['catalogs_new']
                    cat_found = False
                    for c in catalogs:
                        if c['supplier_code'] == supplier_code:
                            cat_found = True
                    if not cat_found:
                        zinc20_data[identifier]['catalogs_new'].append({'supplier_code': supplier_code, 'purchasibility': purchasibility})
        data20 = list(zinc20_data.values())
    return data20

@celery.task( default_retry_delay=30,
    max_retries=15,
    soft_time_limit=10)
def search20(zinc20):
    return zinc20

@celery.task
def mergeSubstanceResults(results):
    results_final = []
    error_logs = []
    if results:
        for result in results:
            results_final.extend(result['items'])
    if len(error_logs) > 0:
        send_search_log(error_logs)
    return results_final

@celery.task
def vendorSearch(vendor_ids):
    result = {}
    t_start = time.time()

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
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    # output fmt: VENDOR CAT_CONTENT_ID MACHINE_ID
                    get_vendor_results_antimony(data_file, search_curs, output_file, missing_file)
                except psycopg2.OperationalError as e:
                    print("failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database))
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
                    #printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
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
                #printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                search(p_id_prev, data_file, tf_inter, missing_file)
                data_file.seek(0)
                data_file.truncate()
                
        t_elapsed = time.time() - t_start
        #printProgressBar(total_length, total_length, prefix = "", suffix="done searching sb!", length=50, t_elapsed=t_elapsed)
        tf_inter.flush()
        
        missing_file.seek(0)
        
        result["missing"] = missing_file.read().split("\n")
                
        # ========== SECOND SORT PROC- SEARCH SN =============
        with subprocess.Popen(["/usr/bin/sort", "-k3", "-S{}".format(sort_mem_arg), tf_inter.name], stdout=subprocess.PIPE) as sort_proc:
            def search(p_id, data_file, output_file):
                search_conn = None
                try:
                    data_file.flush()
                    data_file.seek(0)
                    search_database = get_conn_string(p_id)
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    t_elapsed = time.time() - t_start
                    get_vendor_results_cat_id(data_file, search_curs, output_file)
                except psycopg2.OperationalError as e:
                    print("failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database))
                    for line in data_file:
                        vendor, cat_content_id = line.strip().split()
                        tokens = ["_null_", "_null_", "_null_", vendor, "_null_"]
                        output_file.write('\t'.join(tokens) +'\n')
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
                    #printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
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
                #printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                search(p_id_prev, data_file, output_file)
    
        t_elapsed = time.time() - t_start
        #printProgressBar(total_length, total_length, prefix = "", suffix="done searching sn!", length=50, t_elapsed=t_elapsed)
        
        output_file.seek(0)
        result["found"] = []
        for line in output_file.readlines():
            for line in json.loads(line):
                result["found"].append(line)

        return result
        #printProgressBar(total_l
    
@celery.task
def getSubstanceList(zinc_ids, get_vendors=True):
    t_start = time.time()

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
                    search_conn = psycopg2.connect(search_database, connect_timeout=1)
                    search_curs = search_conn.cursor()
                    t_elapsed = time.time() - t_start
                    if get_vendors:
                        get_vendor_results(data_file, search_curs, output_file, tranches_internal)
                    else:
                        get_smiles_results(data_file, search_curs, output_file, tranches_internal)
                        
                except psycopg2.OperationalError as e:
                    print("failed to connect to {}, the machine is probably down. Going to continue and collect partial results.".format(search_database))
                    tranches_internal_rev = {t[1] : t[0] for t in tranches_internal.items()}
                    for line in data_file:
                        sub_id, tranche_id_int = line.split()
                        sub_id = int(sub_id)
                        tranche = tranches_internal_rev[int(tranche_id_int)]
                        tokens = ["_null_", get_zinc_id(sub_id, tranche), tranche] + (2 if get_vendors else 0) * ["_null_"]
                        missing_file.write('\t'.join(tokens) +'\n')
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
                    #printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)
                    
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
                #printProgressBar(curr_size, total_length, prefix = "", suffix=p_id_prev, length=50, t_elapsed=t_elapsed, projected=projected_size)

                search(p_id_prev, data_file, output_file, tranches_internal)
                
        t_elapsed = time.time() - t_start
        output_file.seek(0)
        result["found"] = []
        for line in output_file.readlines():
            try:
                for line in json.loads(line):
                    result["found"].append(line)
            except:
                print()

        missing_file.seek(0)
        result["missing"] = missing_file.read().split("\n")
        return result
        #printProgressBar(total_length, total_length, prefix = "", suffix="done searching sn!", length=50, t_elapsed=t_elapsed)

def get_smiles_results(data_file, search_curs, output_file, tranches_internal):
    search_curs.execute("create temporary table cb_sub_id_input (sub_id bigint, tranche_id_orig smallint)")
    search_curs.copy_from(data_file, 'cb_sub_id_input', sep='\t', columns=['sub_id', 'tranche_id_orig'])
    search_curs.execute("create temporary table cb_sub_output (smiles text, sub_id bigint, tranche_id smallint, tranche_id_orig smallint)")
    search_curs.execute("call get_some_substances_by_id('cb_sub_id_input', 'cb_sub_output')")
    search_curs.execute("select smiles, sub_id, tranche_id_orig from cb_sub_output")

    parse_tin_results(search_curs, output_file, tranches_internal)

def get_vendor_results(data_file, search_curs, output_file, tranches_internal):
    search_curs.execute("create temporary table cb_sub_id_input (sub_id bigint, tranche_id_orig smallint)")
    search_curs.copy_from(data_file, 'cb_sub_id_input', sep='\t', columns=['sub_id', 'tranche_id_orig'])
    search_curs.execute("create temporary table cb_pairs_output (smiles text, sub_id bigint, tranche_id smallint, supplier_code text, cat_content_id bigint, cat_id_fk smallint, tranche_id_orig smallint)")
    search_curs.execute("call cb_get_some_pairs_by_sub_id()")
    search_curs.execute("select smiles, sub_id, tranche_id_orig, supplier_code, catalog.short_name from cb_pairs_output left join catalog on cb_pairs_output.cat_id_fk = catalog.cat_id")
    
    parse_tin_results(search_curs, output_file, tranches_internal)
    
def get_vendor_results_antimony(data_file, search_curs, output_file, missing_file):
    search_curs.execute("create temporary table tq_in (supplier_code text)")
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
    search_curs.copy_from(data_file, 'cb_vendor_input', sep=',', columns=['supplier_code'])
    search_curs.execute("create temporary table cb_pairs_output (smiles text, sub_id bigint, tranche_id smallint, supplier_code text, cat_content_id bigint, cat_id smallint)")
    search_curs.execute("call cb_get_some_pairs_by_vendor()")
    search_curs.execute("select smiles, sub_id, tranches.tranche_name, supplier_code, catalog.short_name from cb_pairs_output left join tranches on cb_pairs_output.tranche_id = tranches.tranche_id left join catalog on cb_pairs_output.cat_id = catalog.cat_id")
    
    parse_tin_results(search_curs, output_file)

    
def parse_tin_results(search_curs, output_file, tranches_internal= None):
    output = []
    ids = {}

    if tranches_internal:
        tranches_internal_rev = { t[1] : t[0] for t in tranches_internal.items() }
        
    results = search_curs.fetchmany(5000)
    while len(results) > 0:
        for result in results:
            smiles          = result[0] or "_null_"
            sub_id          = result[1]
            if smiles:  
                if tranches_internal:
                    tranche_id_orig = result[2]
                    tranche_name    = tranches_internal_rev[tranche_id_orig]
                else:
                    tranche_name = result[2]
                    
                supplier_codes   = result[3]
                catalog        = result[4]
                tranche_details = get_compound_details(smiles)
                zinc_id = get_zinc_id(sub_id, tranche_name)
                if not zinc_id in ids:
                    ids[zinc_id] = {
                    "zinc_id":zinc_id, 
                    "sub_id":sub_id, 
                    "smiles":smiles, 
                    "tranche":{
                        "h_num": tranche_name[0:3],
                        "logp": tranche_name[3:4],
                        "mwt": tranche_name[4:5],
                        "p_num": tranche_name[3:]
                    },
                    "supplier_code": [supplier_codes], 
                    "catalogs": [{"catalog_name": catalog}], 
                    "tranche_details": tranche_details
                    }
                else:
                    if catalog:
                        ids[zinc_id]["catalogs"].append({
                            "catalog_name": catalog
                        })
                        ids[zinc_id]["supplier_code"].append(supplier_codes)
        results = search_curs.fetchmany(5000)
        
    output = list(ids.values())
    output_file.write(json.dumps(output) + "\n")
    output_file.flush()