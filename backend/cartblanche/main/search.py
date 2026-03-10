import re
import uuid
from flask import Blueprint
import random
from flask import request, abort, make_response, redirect, url_for, jsonify

from celery.result import AsyncResult, GroupResult
from cartblanche import celery
from cartblanche.data.tasks import start_search_task
from cartblanche.data.tasks.search_zinc import getSubstanceList, zinc20search, mergeResults, vendorSearch, paralellizeZincSearch
from cartblanche.data.tasks.search_smiles import sw_search, filter_sw_results
from cartblanche.data.tasks.get_random import getRandom
from cartblanche.helpers.validation import is_zinc22, filter_zinc_ids
from cartblanche.formatters.format import formatZincResult
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cartblanche.helpers.common import find_molecule, getRole
from cartblanche.helpers.validation import base62

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/saveResult/<task>.<format>', methods=["GET"])
def saveResult(
    task,
    format='json'
):
    task_result = AsyncResult(task, app=celery)
    print(f"Task status: {task_result.status}")
    
    # Check if task exists and is not in a failed/unknown state
    if task_result.status == 'PENDING':
        return {'status': 'PENDING'}
    
    if task_result.status == 'FAILURE':
        return {'status': 'ERROR', 'message': str(task_result.result)}, 500
    
    if not task_result.ready():
        return {'status': 'PENDING'}
    
    try:
        wrapper = task_result.get(timeout=10)
    except Exception as e:
        print(f"Error getting task result: {e}")
        return {'status': 'ERROR', 'message': str(e)}, 500
    
    output_fields = wrapper.get('output_fields')
    task_id = wrapper['id']
    
    # Check if this has a group (zinc22progress)
    group_id = wrapper.get('zinc22progress')
    if group_id:
        group = GroupResult.restore(group_id, app=celery)
        
        if group is None:
            print(f"GroupResult.restore returned None for {group_id}")
            # Try as regular AsyncResult
            inner_task = AsyncResult(group_id, app=celery)
            if inner_task.ready():
                result = inner_task.get(timeout=30)
                data = result if isinstance(result, list) else []
            else:
                return {'status': 'PROGRESS', 'message': 'Group result not available yet'}
        else:
            if not group.ready():
                total = len(group.children) if group.children else 1
                return {'progress': group.completed_count() / total, 'status': 'PROGRESS'}
            
            result = group.get(timeout=60)
            
            # Flatten the results from the group
            data = []
            for i in result:
                if isinstance(i, list):
                    data.extend(i)
                else:
                    data.append(i)
            random.shuffle(data)
    else:
        # Regular task - use AsyncResult
        inner_task = AsyncResult(task_id, app=celery)
        if not inner_task.ready():
            return {'status': 'PENDING'}
        
        result = inner_task.get(timeout=30)
        
        # Handle different result structures
        if isinstance(result, dict):
            data = result.get('zinc22', [])
            if result.get('zinc20'):
                data.extend(result['zinc20'])
            if result.get('missing'):
                data.extend(result['missing'])
            if result.get('zinc22_missing'):
                data.extend(result['zinc22_missing'])
        elif isinstance(result, list):
            data = result
        else:
            data = []
    
    if output_fields:
        data = [dict((k, v) for k, v in x.items() if k in output_fields) for x in data]
        
    return make_response(formatZincResult(data, format), 200)


@search_bp.route('/search/result/<task>', methods=["GET"])
def getResult(task):
    #wrapper contains {task:task, submission:submission}
    inucsf = request.access_route[-1][0:3] == '10.' or  request.access_route[-1][0:8] == '169.230.' or request.access_route[-1][0:8] == '128.218.' or request.access_route[0] == '127.0.0.1'
    wrapper = AsyncResult(task, app=celery)
    try:
        task_info = wrapper.get(timeout=60)
    except:
        return {'progress':0, 'result':[], 'status':wrapper.status}
    
    task = task_info['id']
    submission = task_info['submission'] if inucsf else None

    if task_info.get('zinc22progress'):
        zinc22progress = task_info['zinc22progress']
        zinc22task = AsyncResult(zinc22progress, parent=task, app=celery)
        if zinc22task.status == "PROGRESS" or zinc22task.status == "PENDING" and zinc22task.info:
                return {'progress':(zinc22task.info['current']/zinc22task.info['projected']), 'result':[], 'status':zinc22task.status}

    task = AsyncResult(task, app=celery)
    if task.status == "PROGRESS" or task.status == "PENDING":
        if task.info:
            return {'progress':(task.info['current']/task.info['projected']), 'result':[], 'status':task.status}
       
        return {'progress':0, 'result':[], 'status':task.status}

    elif task.status == "SUCCESS":
        result = task.get()
        
        return {'result':result, 'status':task.status, 'submission':submission, 'inUCSF':inucsf}
    
@search_bp.route('/search/result/<task>.<format>', methods=["GET"])
def downloadResult(task, format='json'):
    #wrapper contains {task:task, submission:submission}
    wrapper = AsyncResult(task, app=celery)
    print("hi")

    task_info = wrapper.get()
    
    task = task_info['id']
    submission = task_info['submission']
    task = AsyncResult(task, app=celery)
    result = task.get()

    response = result['zinc22']
    print(response) 
    if result.get('zinc20'):
        response.extend(result['zinc20'])
        response.extend(result['missing'])
    if result.get('zinc22_missing'):
        response.extend(result['zinc22_missing'])

    return make_response(formatZincResult(response, format), 200)



@search_bp.route('/getSubstance/<identifier>', methods=["GET","POST"])
@search_bp.route('/substance/<identifier>.<format>', methods=["GET","POST"])
def search_substance(identifier, data = None, format = 'json'):
    data = find_molecule(identifier, data)
    
    if data:
        
        if request.method == "POST":
            return make_response(formatZincResult([data], format), 200)
        if data.get('db'):
            return make_response(formatZincResult(data, format), 200)
        else:
            return make_response(formatZincResult(data, format), 400)
    else:
        abort(404)


@search_bp.route('/substances.<format>', methods=["POST"])
def search_substances(file = None, data = None, format = 'json', ids = [], output_fields=["smiles", "zinc_id"]): 
    ids = []
    getVendors = True
    if 'zinc_ids' in request.files:
        file = request.files['zinc_ids'].read().decode()
        file = [x for x in re.split(r'\n|\r|(\r\n)', file) if x!='' and x!= None]
        ids.extend(file)

    if request.form.get('smiles_only'):
        getVendors = False
        

    if request.form.get('zinc_ids'):
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', request.form['zinc_ids']) if x!='']
        ids.extend(textDataList)
   
    zinc22, zinc20, discarded = filter_zinc_ids(ids)
   
    if len(zinc22) == 0 and len(zinc20) == 0:
        return "No Valid ZINC IDs, please try again", 400
    zinc20tasks = zinc20search.si(zinc20)
    task_id_progress = str(uuid.uuid4())
    #generates signature objects for each task
    task = [
        paralellizeZincSearch.si(zinc22,  getRole(), discarded, getVendors, task_id_progress=task_id_progress ), zinc20tasks
    ] 
    #merges the results of the zinc20 and zinc22 searches
    callback = mergeResults.s()
    if request.form.get('output_fields'):
        
        output_fields = request.form.get('output_fields').replace(' ', '').split(',')

    if not request.form.get('synchronous'):
        #starts the tasks and returns the task id
        task = start_search_task.delay(task,ids, callback, task_id_progress=task_id_progress, output_fields=output_fields)
        
        return make_response({'task':task.id}, 200)
    else:
        task = start_search_task.delay(task,ids, callback)
        task = AsyncResult(task.id, app=celery)
        result = task.get()

        task = result['id']
        task = AsyncResult(task, app=celery)
        res = task.get()

        result = res['zinc22']
        if res.get('zinc20'):
            result.extend(res['zinc20'])

            if output_fields:
        
                result = [dict((k, v) for k, v in x.items() if k in output_fields) for x in result]
        
        return make_response(formatZincResult(result, format), 200)
    
    

@search_bp.route('/catitems.<format>', methods=["GET","POST"])
def search_catitems(ids=[], data = None, format = 'json', file = None):
    ids = []
    if 'supplier_codes' in request.files:
        file = request.files['supplier_codes'].read().decode()
        file = [x for x in re.split(r'\n|\r|(\r\n)', file) if x!='' and x!= None]
        ids.extend(file)
    
    if request.form.get('supplier_codes'):
        data = request.form['supplier_codes']
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        ids.extend(textDataList)
    
    if len(ids) == 0:
        return "No Valid Supplier Codes, please try again", 400
    
    task = vendorSearch.s(ids)
    task = start_search_task.delay(task,ids)

    if request.method == "POST":
        return {"task": task.id}
    else:
        res= task.get()['id']
        res = AsyncResult(res, app=celery).get("zinc22")
        return make_response(formatZincResult(res, format), 200)


@search_bp.route('/smiles.<format>', methods=["GET","POST"])
def search_smiles(ids=[], data = None, format = 'json', file = None, adist = 0, dist=0):
    zinc20 = False
    zinc22 = False
    ids = []
    if 'smiles' in request.files:
        file = request.files['smiles'].read().decode()
        file = [x for x in re.split(r'\n|\r|(\r\n)', file) if x!='' and x!= None]
        ids.extend(file)
    
    if request.form.get('smiles'):
        data = request.form['smiles']
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', data) if x!='']
        ids.extend(textDataList)

    if request.form.get('adist'):
        adist = request.form['adist']
    if request.form.get('dist'):
        dist = request.form['dist']

    if request.form.get('database'):
        database = request.form['database']
        if 'zinc20' in database:
            zinc20 = True
        if 'zinc22' in database:
            zinc22 = True
    else:
        zinc20 = False
        zinc22 = True
    submission = ids
 
    ids = '\n'.join(ids)
    dist = 3 if int(dist) > 3 else int(dist)
    adist = 3 if int(dist) > 3 else int(adist)

    if len(ids) == 0:
        return "No Valid SMILES, please try again", 400

    #this task id is used to track the progress of the search, between the sw search and the zinc22 search. need to add zinc20 search progress
    task_id_progress = str(uuid.uuid4())
    
    # sw search => filter results => zinc22/20 search
    task = [sw_search.s(ids, dist, adist, zinc22, zinc20, task_id_progress), filter_sw_results.s(getRole(), task_id_progress=task_id_progress)]
    
    task = start_search_task.delay(task, submission, task_id_progress=task_id_progress)
    
    if not request.form.get('synchronous'):
        #starts the tasks and returns the task id
        return make_response({'task':task.id}, 200)
    else:
        task = start_search_task.delay(task, submission)
        task = AsyncResult(task.id, app=celery)
        res = task.get("id")
        task = res['id']
        task = AsyncResult(task, app=celery)
        
        #get the results
        res = task.get()
        
        if res.get('zinc22'):
            results = res['zinc22']
        else:
            results = []
        
        if res.get('zinc20'):
            results.extend(res['zinc20'])
        
        return make_response(formatZincResult(results, format), 200)
   
@search_bp.route('/substance/random/<jobid>.<format>', methods=["GET"])
def random_substance_status(jobid, format = "json"):

    task = AsyncResult(jobid, app=celery)
    if not task.ready():
        return {'progress':0, 'status':task.status}
    
    result = task.get()
    id = result.get('zinc22progress')
    if not id:
        return {'progress':0, 'status':'ERROR', 'message':'No group id found for this task'}
    group = GroupResult.restore(id, app=celery)

    if group is None:
        print("GroupResult.restore returned None")
        return {'status': 'ERROR', 'message': 'Could not restore group result'}
    
    if not group.ready():
        total = len(group.children)
        print(group.completed_count()/total)
        return {'progress':group.completed_count()/total, 'status':'PROGRESS'}
    
    result = group.get()
    print(result)
    
    res = []
    #randomize results
    for i in result:
            res.extend(i)

    random.shuffle(res)
    res = formatZincResult(res, format)
    
    return { 'result':res, 'status':'SUCCESS'}
    
    # return {'progress':0, 'status':task.status}

@search_bp.route('/substance/random.<format>', methods=["GET", "POST"])
def random_substance(format = 'json', subset = None):
    count = request.form['count']
  
    if request.form.get('subset'):

        subset = request.form['subset']

    if subset == 'none':
        subset = None
    
    task = getRandom(subset, count)

    if request.method == "POST":
        return {"task": task}
    else:
        # res= task.get()['id']
        res = AsyncResult(task, app=celery).get()
        res = AsyncResult(res['id'], app=celery).get()
        return make_response(formatZincResult(res, format), 200)



