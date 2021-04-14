from app.data.models.tranche import TrancheModel
from app.data.models.server_mapping import ServerMappingModel
from app.data.models.ip_address import IPAddressModel
from app.data.models.port_number import PortNumberModel
import re
from sqlalchemy import func


# def setUrl(zinc_id: str):
#     url = getTINUrl(zinc_id)
#     if url:
#         print("Setting TIN URL: ", url)
#         current_app.config['TIN_URL'] = url

def getAllUniqueTINServers():
    urls = []
    server_mappings_fk = ServerMappingModel.query.with_entities(
        func.min(ServerMappingModel.sm_id).label("sm_id"),
        ServerMappingModel.ip_fk,
        ServerMappingModel.port_fk
    ).group_by(ServerMappingModel.ip_fk, ServerMappingModel.port_fk).subquery()

    server_mappings = ServerMappingModel.query.filter(ServerMappingModel.sm_id == server_mappings_fk.c.sm_id).all()

    for sm in server_mappings:
        urls.append("{}:{}".format(sm.ip_address.ip, sm.port_number.port))

    return urls

def getAllTINUrl():
    urls = {}

    tranches = TrancheModel.query.with_entities(
        func.min(TrancheModel.tranche_id).label('tranche_id'),
        TrancheModel.mwt.label('mwp'),
        TrancheModel.logp.label('logp'),
        func.min(TrancheModel.server_mapping_fk).label('server_mapping_fk')
    ).group_by(TrancheModel.mwt, TrancheModel.logp).subquery()

    server_mappings = ServerMappingModel.query.with_entities(
        tranches.c.mwp,
        tranches.c.logp,
        ServerMappingModel
    ).join(
        tranches,
        ServerMappingModel.sm_id == tranches.c.server_mapping_fk
    ).join(
        IPAddressModel,
        ServerMappingModel.ip_fk == IPAddressModel.ip_id
    ).join(
        PortNumberModel,
        ServerMappingModel.port_fk == PortNumberModel.port_id
    ).all()

    for sm in server_mappings:
        urls["{}{}".format(sm[0], sm[1])] = "{}:{}".format(sm[2].ip_address, sm[2].port_number)
    return urls


def getSingleTINUrl(zinc_id: str):
    pattern = "^ZINC[a-zA-Z]{2}[0-9a-zA-Z]+"
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