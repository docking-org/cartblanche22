from cartblanche.data.models.tranche import TrancheModel


import re
from sqlalchemy import func
from config import Config
from rdkit.Chem import MolFromSmiles
from rdkit.Chem.Descriptors import MolWt
from rdkit.Chem.Descriptors import MolLogP
from rdkit.Chem.SaltRemover import SaltRemover
from rdkit.Chem.inchi import MolToInchi
from rdkit.Chem.inchi import MolToInchiKey
from rdkit import RDLogger
import os
lg = RDLogger.logger()
lg.setLevel(RDLogger.CRITICAL) 


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

def cvt(ustring):
    l = []
    for uc in ustring:
        l.append(chr(ord(uc) & 0xFF)) # low order byte
        l.append(chr((ord(uc) >> 8) & 0xFF)) # high order byte
    return ''.join(l)


def get_compound_details(smiles):
    smiles = smiles.encode('ascii')
    smiles = smiles.replace(b'\x01', b'\\1')
    smiles = smiles.decode()
    
    m = MolFromSmiles(smiles)
  
 
    heavy_atoms = round(m.GetNumHeavyAtoms(), 3)
    mwt = round(MolWt(m), 3)
    logp = round(MolLogP(m), 3)
    inchi = MolToInchi(m)
    inchikey = MolToInchiKey(m)
    details = {
        'heavy_atoms': heavy_atoms,
        'mwt': mwt,
        'logp': logp,
        'inchi': inchi,
        'inchikey': inchikey
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

digits="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
logp_range="M500 M400 M300 M200 M100 M000 P000 P010 P020 P030 P040 P050 P060 P070 P080 P090 P100 P110 P120 P130 P140 P150 P160 P170 P180 P190 P200 P210 P220 P230 P240 P250 P260 P270 P280 P290 P300 P310 P320 P330 P340 P350 P360 P370 P380 P390 P400 P410 P420 P430 P440 P450 P460 P470 P480 P490 P500 P600 P700 P800 P900".split(" ")
#logp_range_rev={e:i for i, e in enumerate(logp_range)}
digits_map = { digit : i for i, digit in enumerate(digits) }
b62_table = [62**i for i in range(12)]

def base62_rev(s):
    tot = 0
    for i, c in enumerate(reversed(s)):
        val = digits_map[c]
        tot += val * b62_table[i]
    return tot

def get_sub_id(zinc_id):
    return base62_rev(zinc_id[8:])

def get_zinc_id(sub_id, tranche_name):
    if not tranche_name:
        return "ZINC" + "??00" + "{:0>8s}".format(base62(sub_id))
    hac = digits[int(tranche_name[1:3])]
    lgp = digits[logp_range.index(tranche_name[3:])]
    zid = "ZINC" + hac + lgp + "00" + "{:0>8s}".format(base62(sub_id))
    return zid

def get_tranche(zinc_id):
    try:
        hac = base62_rev(zinc_id[4])
        lgp = base62_rev(zinc_id[5])
        tranche = "H{:>02d}{}".format(hac, logp_range[lgp])
        return tranche
    except:
        return "fake"

def get_conn_string(partition_host_port, db='tin', user='tinuser'):
    host, port = partition_host_port.split(':')
    
    if host == os.uname()[1].split('.')[0]:
        host = "localhost"

    return "postgresql://{0}@{1}:{2}/{3}".format(user, host, port, db)

def get_tin_partition(zinc_id, tranche_map):
    return tranche_map.get(get_tranche(zinc_id)) or "fake"

def is_zinc22(identifier):
 
    if not 'ZINC' in identifier:
        if 'CSS' in identifier or '-' in identifier:
            return False
    
    if '-' in identifier:
        return True
    
    if identifier[0:1].upper() == 'C':
        identifier = identifier.replace('C', 'ZINC')
    
    if identifier[4:6] == '00':
        return False
    
    elif identifier.isnumeric():
        return False
   
    elif identifier[0:4].upper() == 'ZINC':
        if identifier[4:6].isnumeric():
            return False
        else:
            return True
    else:
        return None

    


    
# a regex to identify the dataset of a molecule
dataset_regex = {
    "Enamine_M": "m_.*|Z[0-9]{8}|PV-[0-9]{12}|Z[0-9]{10}",
    "Enamine_S": "s_.*",
}


def identify_dataset(identifier):
    for regex in dataset_regex:
        if re.match(dataset_regex[regex], identifier):
            return regex


def filter_zinc_ids(ids):
    zinc22 = []
    zinc20 = []
    discarded = []
    

    for identifier in ids:
        if is_zinc22(identifier) is True:
            zinc22.append(identifier)
        elif is_zinc22(identifier) is False:
            if 'ZINC' in identifier and not identifier.split('ZINC')[1].isnumeric():
                zinc22.append(identifier)
            else:   
                zinc20.append(identifier)
        else:
            discarded.append(identifier)
    print("ZINC22: {}, ZINC20: {}, Discarded: {}".format(len(zinc22), len(zinc20), len(discarded)))
    return zinc22, zinc20, discarded