from cartblanche.helpers.validation import is_zinc22, filter_zinc_ids
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cartblanche.data.tasks.search_zinc import getSubstanceList, zinc20search, mergeResults, vendorSearch

from cartblanche.data.models.users import Users
def find_molecule(identifier, data=None, db=None, smiles=None):
    print(is_zinc22 (identifier))
    if is_zinc22(identifier) :
        task = getSubstanceList.delay([identifier], getRole())
        res = task.get()
    
        logs = res['zinc22']

        if len(res['zinc22']) == 0:
            return None
        data = res['zinc22'][0]
    elif 'ZINC' in identifier:
        task = zinc20search.delay(identifier)
        res = task.get()

        if res:
            data = res
        else:
            return None
    else:
        
        if not db:
            return None
        data = {
            'identifier': identifier,
            'catalogs': [],
            'db': db,
            'smiles': smiles
        }

    return data

@jwt_required(optional=True)
def getRole(current_user = None):
    user_id = get_jwt_identity()
    if user_id:
        current_user = Users.query.filter_by(id=user_id).first()
    
    if current_user and current_user.has_roles('ucsf'):
        role = 'ucsf'
    else:
        role = 'public'
    
    return role
         
