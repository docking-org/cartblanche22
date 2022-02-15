from app.main import application

from app.main.search import search_byzincid
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, reqparse

from app.data.resources.substance import SubstanceList
from flask import render_template, request, json, jsonify, flash, Flask, redirect,g 

from app.data.models.tranche import TrancheModel

from app.helpers.validation import base10, get_all_tin_url, get_all_unique_tin_servers, base62, get_new_tranche, get_compound_details, antimony_hashes_to_urls, get_tin_urls_from_ids, get_tin_urls_from_tranches

from app.helpers.representations import OBJECT_MIMETYPE_TO_FORMATTER
from flask import jsonify, current_app, request, make_response
from collections import defaultdict
from app.data.resources.substance import SubstanceModel
from flask_csv import send_csv
import time

from gevent import monkey
    # from psycogreen.gevent import patch_psycopg
    #
#monkey.patch_all(subprocess=True, ssl=False)

import requests
from datetime import datetime
import itertools
import re

from app import celery_worker
from app.celery_worker import celery, flask_app, db
from celery import group, chord
from celery.result import AsyncResult
from app.email_send import send_search_log
import ast
import psycopg2
import io
import hashlib

@application.route('/search/result_zincsearch', methods=['GET'])
def search_result():
    if request.method == 'GET':
        data = request.args.get("task")
        
        task = AsyncResult(data)
        data = task.get()

        list20 = data[0]
        task22 = data[1]
        list22 = []
        
        if task22 != None:
            task = AsyncResult(task22)
            list22 = task.get()
            
        if(len(list22) == 0 and len(list20) == 0):
            return render_template('errors/search404.html', href='/search/search_byzincid', header="We didn't find those molecules in the Zinc22 database. Click here to return"), 404
        return render_template('search/result_zincsearch.html', data22=list22, data20=list20)

@application.route('/search/result_suppliersearch', methods=['GET'])
def search_result_supplier():

    antimony_task = AsyncResult(request.args.get('task'))
    tinsearch_task = AsyncResult(antimony_task.get())

    result = tinsearch_task.get()

    if len(result) == 0:
        return render_template('errors/search404.html', href='/search/search_by_suppliercode', header="We didn't find those codes in the Zinc22 database. Click here to return")
    return render_template('search/result_zincsearch.html', data22=result, data20=[])


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
            task = SearchJobSupplier.generate_code_search_tasks(codes)
        except Exception as e:
            print(e)
        return redirect('/search/result_suppliersearch?task={}'.format(task))

    def generate_code_search_tasks(codes):
        url_to_codes_map = {}
        hashes = [hashlib.sha256(code.encode('utf-8')).digest()[-2:] for code in codes]
        urls = antimony_hashes_to_urls(hashes)
        for code, hashv in zip(codes, hashes):
            hashv = hex(int.from_bytes(hashv, "little"))[-2:]
            url = urls[hashv]
            if not url_to_codes_map.get(url):
                url_to_codes_map[url] = [code]
            else:
                url_to_codes_map[url].append(code)
        print(urls)
        taskList = []
        for url, codes in url_to_codes_map.items():
            url = url.replace('+psycopg2', '')
            taskList.append(getCodes.s(url, codes))

        result = chord(taskList)(mergeCodeResultsAndSubmitTinSupplierJobs.s())
        return result.id 

class SearchJobSubstance(Resource):

    def post(self):
        data = request.form['myTextarea']
        file = request.files['zincfile'].read().decode("utf-8")
        file = file.split("\n")
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        ids = file + textDataList

        zinc22, zinc20, discarded = SearchJobSubstance.filter_zinc_ids(ids)
        print(zinc22, zinc20, discarded)

        try:
            task = chord([search20.s(zinc20=zinc20), getSubstanceList.s(zinc22)])(mergeResults.s())
        except Exception as e:
            print("err", e)
        
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
                
            if identifier.isnumeric() or identifier[4:6] == '00':
                zinc20.append(identifier)
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

@celery.task
def search20(zinc20):
    monkey.patch_all(subprocess=True, ssl=False)
    zinc20_response = None
    data20 = None
    if len(zinc20) > 0:
        zinc20_files = {
            'zinc_id-in': zinc20,
            'output_fields': "zinc_id supplier_code smiles substance_purchasable"
        }
        zinc20_response = requests.post("https://zinc15.docking.org/catitems.txt", data=zinc20_files)

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

b62_digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
logp_range="M500 M400 M300 M200 M100 M000 P000 P010 P020 P030 P040 P050 P060 P070 P080 P090 P100 P110 P120 P130 P140 P150 P160 P170 P180 P190 P200 P210 P220 P230 P240 P250 P260 P270 P280 P290 P300 P310 P320 P330 P340 P350 P360 P370 P380 P390 P400 P410 P420 P430 P440 P450 P460 P470 P480 P490 P500 P600 P700 P800 P900".split(" ")
logp_range_map={b62_digits[i]:e for i, e in enumerate(logp_range)}
logp_range_map_rev={e:b62_digits[i] for i, e in enumerate(logp_range)}
@celery.task
def getSubstanceList(zinc_ids):
    #SEARCH STEP 3

    zinc_ids = [(base10(zinc_id), "H{:02d}{}".format(b62_digits.index(zinc_id[4]), logp_range_map[zinc_id[5]])) for zinc_id in zinc_ids]
    tranche_to_url_map = get_tin_urls_from_tranches([zinc_id[1] for zinc_id in zinc_ids])
    #urls = get_all_tin_url()
    url_to_ids_map = {}

    for zinc_id in zinc_ids:

        url = tranche_to_url_map.get(zinc_id[1])
        if not url:
            print("tranche url not found!", zinc_id)
            continue
        if not url_to_ids_map.get(url):
            url_to_ids_map[url] = [zinc_id]
        else:
            url_to_ids_map[url].append(zinc_id)
    #if not url:
            #    print("url not found", zinc_id)
            #    continue
            #hac = b62_digits.index(zinc_id[4])
            #logp = logp_range[zinc_id[5]]
            #tranche = "H{:02d}{}".format(hac, logp)

            #zinc_id = (base10(zinc_id), tranche)

            #if not url_to_ids_map.get(url):
            #    url_to_ids_map = [zinc_id]
            #else:
            #    url_to_ids_map.append(zinc_id)

            # pattern = "^ZINC[a-zA-Z]{2}[0-9a-zA-Z]+"
            #pattern = "^ZINC[1-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z]+"
            #if not url or not re.match(pattern, zinc_id):
            #    print("url or zinc_id not found", zinc_id)
            #    continue

    print("TIN URLS ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    for k, v in url_to_ids_map.items():
        print(k, len(v))

    #SEARCH STEP 4, DO REQUEST FOR ALL URLS
    taskList = []
    for url, ids in url_to_ids_map.items(): 
        
        url = url.replace('+psycopg2', '')
        task = getSubstance.s(url, ids)
        taskList.append(task)

    result = chord(taskList)(mergeSubstanceResults.s())

    return result.id

@celery.task
def mergeSubstanceResults(results):
    results_final = []
    error_logs = []
    for result in results:
        #if result['search_info']['not_found_ids'] != "All found" and application.config['EMAIL_ZINCSEARCH_ERROR_LOGS']:
        #    error_logs.append(result['search_info'])
        results_final.extend(result['items'])
    if len(error_logs) > 0:
        send_search_log(error_logs)
    return results_final

@celery.task
def getSubstance(dsn, ids, timeout=10):
    tstart = time.time()
    conn = psycopg2.connect(dsn, connect_timeout=timeout)
    curs = conn.cursor()

    # get tranche information from db (could streamline, but it's not an expensive operation)
    curs.execute("select tranche_name, tranche_id from tranches")
    trancheidmap = {}
    tranchenamemap = {}
    for trancheobj in curs.fetchall():
        tranchename = trancheobj[0]
        trancheid = trancheobj[1]
        trancheidmap[tranchename] = trancheid
        tranchenamemap[trancheid] = tranchename

    if len(ids) > 5000:
        # create a temporary table to hold our query data
        curs.execute(
            "CREATE TEMPORARY TABLE temp_query (\
                sub_id bigint,\
                tranche_id smallint\
            )"
        )

        # format the query data and copy over to db
        query_data = '\n'.join(["{},{}".format(id[0], trancheidmap[id[1]]) for id in ids])
        query_fileobj = io.StringIO(query_data)
        curs.copy_from(query_fileobj, 'temp_query', sep=',', columns=('sub_id', 'tranche_id'))

        # perform query to select all desired information from data
        curs.execute("\
            select ttt.smiles, ttt.sub_id, ttt.tranche_id, ttt.supplier_code, short_name from (\
                select sb.smiles, sb.sub_id, sb.tranche_id, tt.supplier_code, tt.cat_id_fk from (\
                    select cc.cat_content_id, cc.supplier_code, cc.cat_id_fk, t.sub_id_fk, t.tranche_id from (\
                        select cat_content_fk, sub_id_fk, cs.tranche_id from temp_query AS tq(sub_id, tranche_id), catalog_substance AS cs where cs.sub_id_fk = tq.sub_id and cs.tranche_id = tq.tranche_id\
                    ) AS t left join catalog_content AS cc on t.cat_content_fk = cc.cat_content_id\
                ) AS tt left join substance AS sb on tt.sub_id_fk = sb.sub_id and tt.tranche_id = sb.tranche_id\
            ) AS ttt left join catalog AS cat on ttt.cat_id_fk = cat.cat_id order by ttt.sub_id, ttt.tranche_id\
        ")
    else:

        # if looking up small number of codes avoid overhead by using hardcoded VALUES data
        # unsure if this is identical in performance or worse performance than temporary tables
        # I believe there is some overhead associated with processing query lines
        # so it is better at scale to transmit data with copy_from than to hardcode values into query
        curs.execute("\
            select ttt.smiles, ttt.sub_id, ttt.tranche_id, ttt.supplier_code, short_name from (\
                select sb.smiles, sb.sub_id, sb.tranche_id, tt.supplier_code, tt.cat_id_fk from (\
                    select cc.cat_content_id, cc.supplier_code, cc.cat_id_fk, t.sub_id_fk, t.tranche_id from (\
                        select cat_content_fk, sub_id_fk, cs.tranche_id from (values {}) AS tq(sub_id, tranche_id), catalog_substance AS cs where cs.sub_id_fk = tq.sub_id and cs.tranche_id = tq.tranche_id\
                    ) AS t left join catalog_content AS cc on t.cat_content_fk = cc.cat_content_id\
                ) AS tt left join substance AS sb on tt.sub_id_fk = sb.sub_id and tt.tranche_id = sb.tranche_id\
            ) AS ttt left join catalog AS cat on ttt.cat_id_fk = cat.cat_id order by ttt.sub_id, ttt.tranche_id\
        ".format(','.join(["({},{})".format(id[0], trancheidmap[id[1]]) for id in ids])))

    results = curs.fetchall()
    results = [(r[0], r[1], tranchenamemap[r[2]], r[3], r[4]) for r in results]
    conn.rollback()
    conn.close()

    data = format_tin_results(results, trancheidmap)

    tfinish = time.time()
    not_found = [d for d in data if not d['smiles']]

    search_info = {
        'tin_url': dsn,
        'expected_ids': 'Originally searched zinc ids: {}'.format(ids),
        'not_found_ids': 'Not Found: {}'.format(not_found) if len(not_found) > 0 else "All found",
        'elapsed_time': 'It took {:.3f} s'.format((tfinish-tstart))  
    }

    all_data = {'items':data, 'search_info':search_info}

    return all_data

def format_tin_results(results_raw, trancheidmap):
    # extensive result formatting & sorting below
    sub_prev, tranche_prev = None, None
    curr_codes, curr_entry = None, None
    data = []
    for res in results_raw:
        smiles, sub_id, tranche, supplier_code, cat_shortname = res
        # once we arrive at a new substance
        if (sub_id, tranche) != (sub_prev, tranche_prev):
            # flush the entry we were just building to the data stack if it exists
            if curr_entry:
                # uniq-ify the codes before adding to entry
                curr_codes = list(set(curr_codes))
                curr_entry['supplier_code'] = [c[0] for c in curr_codes]
                # catalog information thrown in, all we need is the name
                curr_entry['catalogs'] = [{'catalog_name':c[1]} for c in curr_codes]
                data.append(curr_entry)
            # construct the next entry (minus supplier codes, which we will build as we encounter them)
            curr_codes = []
            tranche_h_digit = b62_digits[int(tranche[1:3])]
            tranche_p_digit = logp_range_map_rev[tranche[3:]]
            hp = tranche_h_digit + tranche_p_digit
            # current html template code expects all this stuff
            # aint gonna argue with it
            curr_entry = {
                'smiles': smiles,
                'zinc_id':"ZINC{}{}".format(hp, base62(sub_id).zfill(10)),
                'sub_id' : sub_id,
                'tranche': get_new_tranche(tranche),
                'tranche_details': get_compound_details(smiles),
                'tranche_id': trancheidmap[tranche]
            }
        if supplier_code:
            curr_codes.append((supplier_code, cat_shortname))
        sub_prev = sub_id
        tranche_prev = tranche
    # finalize & flush the last entry to the stack
    if curr_entry: # this if statement shouldn't be necessary, but keeping it here just in case someone manages to do an empty search
        curr_codes = list(set(curr_codes))
        curr_entry['supplier_code'] = [c[0] for c in curr_codes]
        curr_entry['catalogs'] = [{'catalog_name':c[1]} for c in curr_codes]
        data.append(curr_entry)
    return data

@celery.task
def mergeCodeResultsAndSubmitTinSupplierJobs(results):
    dbid_to_code_map = {}
    for result in results:
        for entry in result:
            cat_content_id, machine_id_fk, supplier_code = entry
            if not dbid_to_code_map.get(machine_id_fk):
                dbid_to_code_map[machine_id_fk] = [(supplier_code, cat_content_id)]
            else:
                dbid_to_code_map[machine_id_fk].append((supplier_code, cat_content_id))
    
    tasklist = []
    dbids_map = get_tin_urls_from_ids(dbid_to_code_map.keys())
    for dbid, codes in dbid_to_code_map.items():
        url = dbids_map[dbid]
        url = url.replace('+psycopg2', '') # this bit is only for sqlalchemy connections, remove it for raw psycopg2 connections
        tasklist.append(getTinSupplier.s(url, codes))
    return chord(tasklist)(mergeSubstanceResults.s()).id

@celery.task
def getCodes(url, codes, timeout=10):
    conn = psycopg2.connect(url, connect_timeout=timeout)
    curs = conn.cursor()

    if len(codes) > 5000:
        curs.execute("CREATE TEMPORARY TABLE temp_query (code varchar)")

        query_data = "\n".join(codes)
        query_fileobj = io.StringIO(query_data)
        curs.copy_from(query_fileobj, 'temp_query', columns=('code'))

        curs.execute("\
            select cat_content_id, machine_id_fk, supplier_code from (\
                select supplier_code, sup_id from temp_query AS tq(code), supplier_codes as sc where tq.code = sc.supplier_code\
            ) AS t left join supplier_map AS sm on t.sup_id = sm.sup_id_fk\
        ")
    else:

        curs.execute("\
            select cat_content_id, machine_id_fk, supplier_code from (\
                select supplier_code, sup_id from (values {}) AS tq(code), supplier_codes AS sc where tq.code = sc.supplier_code\
            ) AS t left join supplier_map AS sm on t.sup_id = sm.sup_id_fk\
        ".format(','.join(['(\'' + c + '\')' for c in codes])))

    results = curs.fetchall()
    uniq_results = set([res[2] for res in results])
    uniq_inputs = set(codes)
    #if len(uniq_results) < len(uniq_inputs):
    #    print("FAILED TO FIND CODES @ {}:".format(url))
    #    print(uniq_inputs.difference(uniq_results))
    conn.rollback()
    conn.close()

    return results

@celery.task
def getTinSupplier(dsn, codes, timeout=10):
    tstart = time.time()
    conn = psycopg2.connect(dsn, connect_timeout=timeout)
    curs = conn.cursor()

    # get tranche information from db (could streamline, but it's not an expensive operation)
    curs.execute("select tranche_name, tranche_id from tranches")
    trancheidmap = {}
    tranchenamemap = {}
    for trancheobj in curs.fetchall():
        tranchename = trancheobj[0]
        trancheid = trancheobj[1]
        trancheidmap[tranchename] = trancheid
        tranchenamemap[trancheid] = tranchename

    if len(codes) > 5000:
        # create a temporary table to hold our query data
        curs.execute(
            "CREATE TEMPORARY TABLE temp_query (\
                cat_content_id bigint,\
                supplier_code varchar,\
            )"
        )

        # format the query data and copy over to db
        query_data = '\n'.join(["{},{}".format(code[1], code[0]) for code in codes])
        query_fileobj = io.StringIO(query_data)
        curs.copy_from(query_fileobj, 'temp_query', sep=',', columns=('cat_content_id', 'supplier_code'))

        # perform query to select all desired information from data
        curs.execute("\
            select ttt.smiles, ttt.sub_id, ttt.tranche_id, ttt.supplier_code, short_name from (\
                select sb.smiles, sb.sub_id, sb.tranche_id, tt.supplier_code, tt.cat_id_fk from (\
                    select cc.cat_content_id, cc.supplier_code, cc.cat_id_fk, t.sub_id_fk, t.tranche_id from (\
                        select cat_content_fk, sub_id_fk, tranche_id from temp_query AS tq, catalog_substance AS cs where cs.cat_content_fk = tq.cat_content_id\
                    ) AS t left join catalog_content AS cc on t.cat_content_fk = cc.cat_content_id\
                ) AS tt left join substance AS sb on tt.sub_id_fk = sb.sub_id and tt.tranche_id = sb.tranche_id\
            ) AS ttt left join catalog AS cat on ttt.cat_id_fk = cat.cat_id order by ttt.sub_id, ttt.tranche_id\
        ")
    else:

        # if looking up small number of codes avoid overhead by using hardcoded VALUES data
        # unsure if this is identical in performance or worse performance than temporary tables
        # I believe there is some overhead associated with processing query lines
        # so it is better at scale to transmit data with copy_from than to hardcode values into query
        curs.execute("\
            select ttt.smiles, ttt.sub_id, ttt.tranche_id, ttt.supplier_code, short_name from (\
                select sb.smiles, sb.sub_id, sb.tranche_id, tt.supplier_code, tt.cat_id_fk from (\
                    select cc.cat_content_id, cc.supplier_code, cc.cat_id_fk, t.sub_id_fk, t.tranche_id from (\
                        select cat_content_fk, sub_id_fk, tranche_id from (values {}) AS tq(cat_content_id, supplier_code), catalog_substance AS cs where cs.cat_content_fk = tq.cat_content_id\
                    ) AS t left join catalog_content AS cc on t.cat_content_fk = cc.cat_content_id\
                ) AS tt left join substance AS sb on tt.sub_id_fk = sb.sub_id and tt.tranche_id = sb.tranche_id\
            ) AS ttt left join catalog AS cat on ttt.cat_id_fk = cat.cat_id order by ttt.sub_id, ttt.tranche_id\
        ".format(','.join(["({},\'{}\')".format(code[1], code[0]) for code in codes])))

    results = curs.fetchall()
    results = [(r[0], r[1], tranchenamemap[r[2]], r[3], r[4]) for r in results]
    #print(results)
    conn.rollback()
    conn.close()

    data = format_tin_results(results, trancheidmap)

    tfinish = time.time()
    not_found = [d for d in data if not d['smiles']]

    search_info = {
        'tin_url': dsn,
        'expected_ids': 'Originally searched codes: {}'.format(codes),
        'not_found_ids': 'Not Found: {}'.format(not_found) if len(not_found) > 0 else "All found",
        'elapsed_time': 'It took {:.3f} s'.format((tfinish-tstart))  
    }

    all_data = {'items':data, 'search_info':search_info}

    return all_data

"""
@celery.task
def getSubstance(args, file_type=None):
    db.choose_tenant(args.get("tin_url"))

    sub_id_list = args.get('sub_ids').split(',')
    zinc_id_list = args.get('zinc_ids').split(',')
    sub_ids = (int(id) for id in sub_id_list)
    sub_ids_len = len(args.get('sub_ids').split(','))

    print("REQUESTED TIN_URL from Substance POST", args.get('tin_url'))
    time1 = time.time()
    try:
        substances = SubstanceModel.query.filter(SubstanceModel.sub_id.in_(sub_ids)).all()
    except Exception as e:
        search_info = {
            'tin_url': args.get('tin_url'),
            'expected_result_count': sub_ids_len,
            'returned_result_count': 0,
            'expected_ids': 'Originally searched zinc ids: {}'.format(zinc_id_list),
            'returned_ids': '================SQL SERVER CONNECTION ERROR==============',
            'not_found_ids': 'Please check {} server connection'.format(args.get('tin_url')),
            'elapsed_time': 'It took {:.3f} s'.format((time.time() - time1) % 60),
            'exception error': str(e)
        }
        return [{'message': 'Couldn\'t connect to db', 'search_info': search_info}]

    time2 = time.time()
    strtime1 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time1))
    strtime2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time2))
    print('{:s} !!!!!!!!!! started at {} and finished at {}. It took {:.3f} s'.format(args.get('tin_url'), strtime1,
                                                                                        strtime2,
                                                                                        (time2 - time1) % 60))
    print("{} server returned {} results and {} result was expecting".format(args.get('tin_url'), len(substances),
                                                                                sub_ids_len))

    data = []
    unmatched = set()
    matched = set()
    for sub in substances:
        data_dict = sub.json()
        sub_id_list.remove(str(data_dict['sub_id']))
        
        if 'output_fields' in args and args.get('output_fields'):

            output_fields = args.get('output_fields').replace(" ", "").split(",")
            output_fields = [i for i in data_dict.keys() if i in output_fields]

            new_dict = {output_field: data_dict[output_field] for output_field in output_fields}
            data_dict = new_dict
        if data_dict['zinc_id'] in zinc_id_list:
            data.append(data_dict)
            matched.add(data_dict['zinc_id'])
        else:
            unmatched.add(data_dict['zinc_id'])

    # if args.get('show_missing') and args.get('show_missing').lower() == 'on':
    #     print("missing sub_ids:", sub_id_list)
    #     return jsonify({args.get('tin_url'): sub_id_list})
    notfound_ids = [id for id in zinc_id_list if id not in matched]

    search_info = {
        'tin_url': args.get('tin_url'),
        'expected_result_count': sub_ids_len,
        'returned_result_count': len(substances),
        'expected_ids': 'Originally searched zinc ids: {}'.format(zinc_id_list),
        'returned_ids': 'Wrong zinc ids returned: {}'.format(unmatched) if unmatched else "All matched",
        'not_found_ids': notfound_ids if notfound_ids else "All found",
        'elapsed_time': 'It took {:.3f} s'.format((time2 - time1) % 60)
    }
    
    if(len(notfound_ids) == 0):
        data.append({'search_info': search_info})
        return data
    else:
        return {'message': 'Not found', 'search_info': search_info}
"""
