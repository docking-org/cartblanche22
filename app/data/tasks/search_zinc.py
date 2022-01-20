from typing import Tuple
from app.main import application

from app.main.search import search_byzincid
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, reqparse
from app.data.resources.substance import SubstanceList
from flask import render_template, request, json, jsonify, flash, Flask, redirect

from app.data.models.tranche import TrancheModel
from werkzeug.datastructures import FileStorage
from app.helpers.validation import base10, get_all_tin_url, get_all_unique_tin_servers

from app.helpers.representations import OBJECT_MIMETYPE_TO_FORMATTER
from flask import jsonify, current_app, request, make_response
from collections import defaultdict
from app.data.resources.substance import SubstanceModel
from flask_csv import send_csv
import time
import requests
from datetime import datetime
import itertools
import re

from app.celery_worker import celery, flask_app, db
from celery import group
from celery.result import allow_join_result, AsyncResult
from app.email_send import send_search_log


@application.route('/search/result_zincsearch', methods=['GET'])
def search_result():
    if request.method == 'GET':
        data = request.args.get("task")
        task = AsyncResult(data)
        list22 = []
        list20 = []
        task_result = task.get()
        result22 = task_result['data22']
        result20 = task_result['data20']
        print(task_result)

        for i in result22:
            if 'message' not in i[0]:
                list22.append(i[0])
        
        if(len(list22) == 0 and len(result20) == 0):
            return render_template('errors/search404.html', href='/search/search_byzincid', header="We didn't find those molecules in the Zinc22 database. Click here to return"), 404
        return render_template('search/result_zincsearch.html', data22=list22, data20=result20)


class SearchJob(Resource):
    def post(self):
        data = request.form['myTextarea']
        file = request.files['zincfile'].read().decode("utf-8")
        file = file.split("\n")
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        args = file + textDataList
        zinc20 = []
        zinc22 = []
        data20 = {}
        discarded = []
        zinc20_response = None
       
        for identifier in args:
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
        
        task = searchByZincId.delay(args=args, zinc22=zinc22, data20 = data20) 
        
        return redirect(('search/result_zincsearch?task={task}'.format(task = task)))


@celery.task
def searchByZincId(args, data20, zinc22, file_type=None):
    textDataList = args
    print("hi!")
    print(data20)
    zinc22_response  = None
    data22_json, data22 = None, None
   
    
    if len(zinc22) > 0:
        files = {
            'zinc_id-in': ','.join(zinc22)
        }
        
        with flask_app.app_context():
            db.choose_tenant("tin")
            zinc22_response = getList(args=files, file_type=None)
            print(zinc22_response)    

    data22= zinc22_response['items']
    
    return {'data22' : data22, 'data20': data20}

    # if data20 or data22:
    #     print(data20)
    #     return render_template('search/result_zincsearch.html', data22_json=json.dumps(data22), data22=data22,
    #                             data20_json=json.dumps(data20), data20=data20)
    # else:
    #     return render_template('errors/search404.html', lines=files, href='/search/search_byzincid',
    #                         header="We didn't find those molecules from Zinc22 database. Click here to return"), 404
    
def getList(args, file_type=None):
    #SEARCH STEP 3

    zinc_ids = sorted(args.get('zinc_id-in').split(','))

    output_fields = ""
    if args.get('output_fields'):
        output_fields = args.get('output_fields')
    dict_ids = defaultdict(list)
    dict_zinc_ids = defaultdict(list)
    dict_subid_zinc_id = defaultdict(list)

    # overlimit_count = 0
    # chunk = 1000
    if args.get('chunk'):
        chunk = args.get('chunk')
    timeout = 15
    if args.get('timeout'):
        timeout = args.get('timeout')

    urls = get_all_tin_url()
    print(zinc_ids)
    for zinc_id in zinc_ids:
        if zinc_id:
            url = urls.get(zinc_id[4:6])
            # pattern = "^ZINC[a-zA-Z]{2}[0-9a-zA-Z]+"
            pattern = "^ZINC[1-9a-zA-Z][0-9a-zA-Z][0-9a-zA-Z]+"
            if not url or not re.match(pattern, zinc_id):
                print("url or zinc_id not found", zinc_id)
                continue
                # return {'message': 'No server is mapped to {}. Please contact with Irwin Lab.'.format(zinc_id)}, 404

            # Commented splitting by chunk size for now
            # Need to fix it
            # if len(dict_ids[url]) > chunk:
            #     dict_ids["{}-{}".format(url, overlimit_count)] = dict_ids[url]
            #     dict_ids[url] = [base10(zinc_id)]
            #     dict_zinc_ids[url] = [zinc_id]
            #     overlimit_count += 1
            # else:
            #     dict_ids[url].append(base10(zinc_id))
            #     dict_zinc_ids[url].append(zinc_id)

            dict_ids[url].append(base10(zinc_id))
            dict_zinc_ids[url].append(zinc_id)
            dict_subid_zinc_id[int(base10(zinc_id))].append(zinc_id)

    for k, v in dict_ids.items():
        print("TIN URLS ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(k, len(v))
       

    #SEARCH STEP 4, DO REQUEST FOR ALL URLS
    results = []
    taskList = []
    for k,v in dict_ids.items():
        data= {
            'sub_ids': ','.join([str(i) for i in v]),
            'zinc_ids': ','.join([str(i) for i in dict_zinc_ids[k]]),
            'tin_url': k.split('-')[0],
            'output_fields': output_fields
        }        
        
        taskList.append(getSubstance.s(args=data))


    #create celery task group, will be executed asynchronously
    tasks = group(taskList)
    task_output = tasks.apply_async()

    with allow_join_result():
        results = task_output.get()
    
    #flat_list = itertools.chain.from_iterable(results)
    data['items'] = list(results)

    # gets search info with 'not found ids' from flat list
    data['search_info'] = [d['search_info'] for d in data['items'] if 'search_info' in d and d['search_info']['not_found_ids'] != 'All found']

    #if len(data['search_info']) > 0:
        #send_search_log(data['search_info'])

    # gets only results from flat list
    data['items'] = [d for d in data['items'] if 'search_info' not in d]
   
    str_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    if file_type == 'csv':
        keys = list(data['items'][0].keys())
        return send_csv(data['items'], "zinc_id_search_{}.csv".format(str_time), keys)
    elif file_type == 'txt':
        Formatter = OBJECT_MIMETYPE_TO_FORMATTER["text/plain"]
        keys = list(data['items'][0].keys())
        formatter = Formatter(fields=keys)
        ret_list = ""
        for line in formatter(data['items']):
            ret_list += line

        download_filename = "search_{}.txt".format(str_time)
        response = make_response(ret_list, 200)
        response.mimetype = "text/plain"
        response.headers['Contnt-Disposition'] = 'attachment; filename={}'.format(download_filename)
        return response
    else:
        return data

   

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
