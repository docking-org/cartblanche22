import re
from flask import Blueprint

from flask import request, abort, make_response, redirect, url_for, jsonify

from celery.result import AsyncResult
from cartblanche.data.tasks import start_search_task
from cartblanche.data.tasks.search_zinc import getSubstanceList, zinc20search, mergeResults, vendorSearch, getzinc20list
from cartblanche.data.tasks.search_smiles import sw_search
from cartblanche.data.tasks.get_random import getRandom
from cartblanche.helpers.validation import is_zinc22, filter_zinc_ids
from cartblanche.formatters.format import formatZincResult
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cartblanche.helpers.common import find_molecule, getRole


search_bp = Blueprint('search', __name__)

@search_bp.route('/search/saveResult/<task>.<format>', methods=["GET"])
def saveResult(
    task,
    format='json'
):
    
    task = AsyncResult(task).get()
    task = task['id']
    task = AsyncResult(task)

    if task:
        result = task.get()
        result = result['zinc22'] + result['zinc20']

        for mol in result:
            best_catalog = None
            #find the best catalog, by shipping time, which is formatted as 'x weeks', so like 6 weeks. split on space, take the first element, convert to int, and sort
            for i in mol['catalogs']:
                if not best_catalog:
                    best_catalog = i
                else:
                    if i.get('price') and best_catalog.get('price'):
                        if int(i['price']) < int(best_catalog['price']):
                            best_catalog = i
            mol['catalogs'] = best_catalog

        
        #return file to download
        return make_response(formatZincResult(result, format), 200)
    else:
        abort(404)


@search_bp.route('/search/result/<task>', methods=["GET"])
def getResult(task):
    #wrapper contains {task:task, submission:submission}
    inucsf = request.access_route[-1][0:3] == '10.' or  request.access_route[-1][0:8] == '169.230.' or request.access_route[-1][0:8] == '128.218.' or request.access_route[0] == '127.0.0.1'
    wrapper = AsyncResult(task)

    task_info = wrapper.get()
    
    task = task_info['id']
    submission = task_info['submission'] if inucsf else None

    if task_info.get('zinc22progress'):
        zinc22progress = task_info['zinc22progress']
        zinc22task = AsyncResult(zinc22progress, parent=task)
        print(zinc22task.status)
        if zinc22task.status == "PROGRESS" or zinc22task.status == "PENDING" and zinc22task.info:
                return {'progress':(zinc22task.info['current']/zinc22task.info['projected']), 'result':[], 'status':zinc22task.status}

    task = AsyncResult(task)
    if task.status == "PROGRESS" or task.status == "PENDING":
        if task.info:
            print(task.info)
            return {'progress':(task.info['current']/task.info['projected']), 'result':[], 'status':task.status}
       
        return {'progress':0, 'result':[], 'status':task.status}

    elif task.status == "SUCCESS":
        result = task.get()
        
        return {'result':result, 'status':task.status, 'submission':submission, 'inUCSF':inucsf}
    
@search_bp.route('/search/result/<task>.<format>', methods=["GET"])
def downloadResult(task, format='json'):
    #wrapper contains {task:task, submission:submission}
    wrapper = AsyncResult(task)

    task_info = wrapper.get()
    
    task = task_info['id']
    submission = task_info['submission']
    task = AsyncResult(task)
    result = task.get()

    response = result['zinc22'] 
    if result.get('zinc20'):
        response.extend(result['zinc20'])
    

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


@search_bp.route('/substances.<format>', methods=["POST", "GET"])
def search_substances(file = None, data = None, format = 'json', ids = [], output_fields=["zinc_id, smiles"]): 
    ids = []
    if 'zinc_ids' in request.files:
        file = request.files['zinc_ids'].read().decode()
        file = [x for x in re.split(r'\n|\r|(\r\n)', file) if x!='' and x!= None]
        ids.extend(file)
    

    if request.form.get('zinc_ids'):
        textDataList = [x for x in re.split(' |, |,|\n, |\r, |\r\n', request.form['zinc_ids']) if x!='']
        ids.extend(textDataList)
   
    zinc22, zinc20, discarded = filter_zinc_ids(ids)
   
    if len(zinc22) == 0 and len(zinc20) == 0:
        return "No Valid ZINC IDs, please try again", 400
    zinc20tasks = [zinc20search.si(zinc20) for zinc20 in zinc20]
    task = [
        getSubstanceList.si(zinc22,  getRole(), discarded ),
    ] + zinc20tasks
    
    callback = mergeResults.s()

    if request.method == "POST":
        task = start_search_task.delay(task,ids, callback)
        return make_response({'task':task.id}, 200)
    else:
        task = start_search_task.delay(task,ids, callback)
        task = AsyncResult(task.id)
        result = task.get()
        task = result['id']
        task = AsyncResult(task)
        res = task.get()
        result = ['zinc22']
        if res.get('zinc20'):
            result.extend(result['zinc20'])

        if request.form.get('output_fields'):
            output_fields = request.form.get('output_fields').split(',')
            result = [{k:v for k,v in i.items() if k in output_fields} for i in result]
        
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
        res = AsyncResult(res).get()
        res  = res['zinc22']
        return make_response(formatZincResult(res, format), 200)


@search_bp.route('/smiles.<format>', methods=["GET","POST"])
def search_smiles(ids=[], data = None, format = 'json', file = None, adist = 0, dist=0):
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
    
    submission = ids
    ids = '\n'.join(ids)
    dist = '4' if int(dist) > 4 else dist
    adist = '4' if int(dist) > 4 else adist

    if len(ids) == 0:
        return "No Valid SMILES, please try again", 400
    
    #sw search for zincids -> zinc22 search for cat info
    task = [sw_search.s(ids, adist, dist), getSubstanceList.s(getRole())]

    
    task = start_search_task.delay(task,submission)

    if request.method == "POST":
        return {"task": task.id}
    else:
        res= task.get()['id']
        res = AsyncResult(res).get()
        res = res['zinc22']

        return make_response(formatZincResult(res, format), 200)
    
@search_bp.route('/substance/random.<format>', methods=["GET", "POST"])
def random_substance(format = 'json', subset = None):

    count = request.form['count']
  
    if request.form.get('subset'):

        subset = request.form['subset']

    if subset == 'none':
        subset = None
    
    task = getRandom.delay(subset, count)
    
    result = task.get()

    return make_response(formatZincResult(result, format), 200)
    