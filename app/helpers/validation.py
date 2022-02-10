from app.data.models.tranche import TrancheModel
from app.data.models.server_mapping import ServerMappingModel
from app.data.models.ip_address import IPAddressModel
from app.data.models.port_number import PortNumberModel
import re
from sqlalchemy import func
from rdkit.Chem import MolFromSmiles
from rdkit.Chem.Descriptors import MolWt
from rdkit.Chem.Descriptors import MolLogP
from rdkit.Chem.SaltRemover import SaltRemover
from rdkit.Chem.inchi import MolToInchi
from rdkit.Chem.inchi import MolToInchiKey
from flask import current_app
import psycopg2
import socket
# from rdkit.Chem.rdMolDescriptors import CalcMolFormula


def get_all_unique_tin_servers():
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

def get_tin_urls_from_ids(ids):
    zinc22_common_url = current_app.config["SQLALCHEMY_BINDS"]["zinc22_common"]
    zinc22_common_url = zinc22_common_url.replace('+psycopg2', '')
    conn = psycopg2.connect(zinc22_common_url, connect_timeout=3)
    tin_id_to_url_map = {}
    with conn.cursor() as curs:
        unique_ids = set(ids)
        curs.execute("select tm.hostname, tm.port, tm.machine_id from (values {}) AS tq(machine_id) left join tin_machines AS tm on tq.machine_id = tm.machine_id".format(','.join(["({})".format(mid) for mid in unique_ids])))
        for res in curs.fetchall():
            host, port, machine_id = res
            host = socket.gethostbyname(host)
            url = "postgresql+psycopg2://tinuser:usertin@{}:{}/tin".format(host, port)
            tin_id_to_url_map[machine_id] = url
    return tin_id_to_url_map

def antimony_hashes_to_urls(hashes):
    zinc22_common_url = current_app.config["SQLALCHEMY_BINDS"]["zinc22_common"]
    zinc22_common_url = zinc22_common_url.replace('+psycopg2', '')
    conn = psycopg2.connect(zinc22_common_url, connect_timeout=3)
    hash_to_url_map = {}
    with conn.cursor() as curs:
        unique_hashes = set(hashes)
        # right now zinc22_common only hold two hex digits, instead of the full 4, so we chop it down here
        unique_hashes = [hex(int.from_bytes(hashv, "little"))[-2:] for hashv in unique_hashes]
        curs.execute(
            "select am.host, am.port, t.hashseq from (\
                select hashseq, partition from (values {}) AS tq(hash) left join antimony_hash_partitions AS ahp on tq.hash = ahp.hashseq\
            ) AS t left join antimony_machines as am on t.partition = am.partition".format(','.join(["(\'{}\')".format(hseq) for hseq in unique_hashes])))
        for res in curs.fetchall():
            host, port, hashseq = res
            if not host:
                continue
            host = socket.gethostbyname(host)
            url_fmtd = "postgresql+psycopg2://antimonyuser@{}:{}/antimony".format(host, port)
            hash_to_url_map[hashseq] = url_fmtd
    return hash_to_url_map

def get_tin_urls_from_tranches(tranches):
    zinc22_common_url = current_app.config["SQLALCHEMY_BINDS"]["zinc22_common"]
    zinc22_common_url = zinc22_common_url.replace('+psycopg2', '')
    conn = psycopg2.connect(zinc22_common_url)
    tranche_to_url_map = {}
    with conn.cursor() as curs:
        unique_tranches = set(tranches)
        curs.execute(
            "select tm.tranche, tm.host, tm.port from (values {}) as tq(tranche) left join tranche_mappings as tm on tq.tranche = tm.tranche\
            ".format(','.join(["(\'{}\')".format(tranche) for tranche in unique_tranches]))
        )
        for res in curs.fetchall():
            tranche, host, port = res
            host = socket.gethostbyname(host)
            tranche_to_url_map[tranche] = "postgresql+psycopg2://tinuser:usertin@{}:{}/tin".format(host, port)
    return tranche_to_url_map

def get_all_tin_url():
    zinc22_common_url = current_app.config["SQLALCHEMY_BINDS"]["zinc22_common"]
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


def get_single_tin_url(zinc_id: str):
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


remover = SaltRemover()
logp_mapping = {
    'M500': '0', 'M400': '1', 'M300': '2', 'M200': '3', 'M100': '4', 'M000': '5',
    'P000': '6', 'P010': '7', 'P020': '8', 'P030': '9', 'P040': 'a', 'P050': 'b', 'P060': 'c', 'P070': 'd',
    'P080': 'e', 'P090': 'f', 'P100': 'g', 'P110': 'h', 'P120': 'i', 'P130': 'j', 'P140': 'k', 'P150': 'l',
    'P160': 'm', 'P170': 'n', 'P180': 'o', 'P190': 'p', 'P200': 'q', 'P210': 'r', 'P220': 's', 'P230': 't',
    'P240': 'u', 'P250': 'v', 'P260': 'w', 'P270': 'x', 'P280': 'y', 'P290': 'z', 'P300': 'A', 'P310': 'B',
    'P320': 'C', 'P330': 'D', 'P340': 'E', 'P350': 'F', 'P360': 'G', 'P370': 'H', 'P380': 'I', 'P390': 'J',
    'P400': 'K', 'P410': 'L', 'P420': 'M', 'P430': 'N', 'P440': 'O', 'P450': 'P', 'P460': 'Q', 'P470': 'R',
    'P480': 'S', 'P490': 'T', 'P500': 'U', 'P600': 'V', 'P700': 'W', 'P800': 'X', 'P900': 'Y', '': 'Z'
}

def get_mwt(h_num):
    if h_num <= 9:
        return h_num
    elif h_num <= 35:
        return chr(h_num + 87)
    else:
        return chr(h_num + 29)

def scale_logp_value(logp):
    if logp < -9.0:
        logp = -9.0
    elif logp > 9.0:
        logp = 9.0
    if logp < 0.0 or logp >= 5.0:
        logp = 100 * int(logp)
    else:
        logp = 10 * int(10 * logp)
    return logp


def get_compound_details(smiles):
    m = MolFromSmiles(smiles)
    heavyAtoms = round(m.GetNumHeavyAtoms(), 3)
    mwt = round(MolWt(m), 3)
    logp = round(MolLogP(m), 3)
    inchi = MolToInchi(m)
    inchi_key = MolToInchiKey(m)
    details = {
        'heavyAtoms': heavyAtoms,
        'mwt': mwt,
        'logp': logp,
        'inchi': inchi,
        'inchi_key': inchi_key
    }
    return details


def get_basic_tranche(smiles):
    mol = MolFromSmiles(smiles)
    if mol:
        if '.' in smiles:
            mol = remover.StripMol(mol)
        logp = MolLogP(mol)
        num_heavy_atoms = mol.GetNumHeavyAtoms()
        if num_heavy_atoms > 99:
            num_heavy_atoms = 99
        sign = 'M' if logp < 0.0 else 'P'
        p_num = "{}{}".format(sign, str(abs(scale_logp_value(logp))).zfill(3))
        tranche_args = {
            'h_num': "H{}".format(str(num_heavy_atoms).zfill(2)),
            'p_num': p_num,
            'mwt': str(get_mwt(num_heavy_atoms)),
            'logp': logp_mapping[p_num]
        }
        return tranche_args
    return {}


def get_new_tranche(tranche):
    h_num = tranche[0:3]
    p_num = tranche[3::]
    hac = int(h_num[1::])
    tranche_args = {
        'h_num': h_num,
        'p_num': p_num,
        'mwt': base62(hac),
        'logp': logp_mapping[p_num]
    }
    return tranche_args
