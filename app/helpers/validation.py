from app.data.models.tranche import TrancheModel
from flask import request, current_app
import re


def setUrl(zinc_id: str):
    url = getTINUrl(zinc_id)
    if url:
        print("Setting TIN URL: ", url)
        current_app.config['TIN_URL'] = url


def getTINUrl(zinc_id: str):
    pattern =  "^ZINC[a-zA-Z]{2}[0-9a-zA-Z]+"
    args = {}
    if re.match(pattern, zinc_id):
        args['mwt'] = zinc_id[4:5]
        args['logp'] = zinc_id[5:6]
        
    trancheQuery = TrancheModel.query
    tranche = trancheQuery.filter_by(**args).first()
    if tranche:
        return tranche.url_string()
    return None


def base10(zinc_id: str):
    zinc_id = zinc_id[7:]
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base10 = 0
    for i, c in enumerate(zinc_id[::-1]):
        base10 += digits.index(c) * pow(62, i)
    return base10
    
def base62(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    b62_str = ""
    while n >= 62:
        n, r = divmod(n, 62)
        b62_str += digits[r]
    b62_str += digits[n]
    return b62_str[::-1]