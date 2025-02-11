from inspect import trace
import psycopg2
from config import Config
from itertools import groupby
from flask import request, make_response
from cartblanche.app import app 
from cartblanche.data.models.tranche import TrancheModel



def URIFormatter(hac, logp, format, add_url, charge, generation):
    if generation != '':
        return "{base_url}zinc22/zinc-22{generation}/{hac}/{hac}{logp}".format(base_url=base_url, add_url=add_url, hac=hac, logp= logp, charge=charge, format=format, generation=generation)
    else:
         return "{}{}{}/{}{}{}.{}".format(base_url, add_url, hac, hac, logp, charge, format)

def WyntonFormatter(hac, logp, format, add_url, charge, generation):
    return "/wynton/group/bks/zinc-22{generation}/{hac}/{hac}{logp}".format(base_url=base_url, add_url=add_url, hac=hac, logp= logp, charge=charge, format=format, generation=generation)
    
def BKSLabFormatter(hac, logp, format, add_url, charge, generation):
    return "/nfs/exd/zinc-22{generation}/{hac}/{hac}{logp}".format(base_url=base_url, add_url=add_url, hac=hac, logp= logp, charge=charge, format=format, generation=generation)    

def AWSFormatter(hac, logp, format, add_url, charge, generation):
    return "s3://zinc3d/zinc-22{generation}/{hac}/{hac}{logp}".format(base_url=base_url, add_url=add_url, hac=hac, logp= logp, charge=charge, format=format, generation=generation)    

def OCIFormatter(hac, logp, format, add_url, charge, generation):
    return "https://objectstorage.us-ashburn-1.oraclecloud.com/n/idrvm4tkz2a8/b/ZINC/o//zinc-22{generation}/{hac}/{hac}{logp}".format(base_url=base_url, add_url=add_url, hac=hac, logp= logp, charge=charge, format=format, generation=generation)    

def DBFormatter(hac, logp, format, add_url, charge, generation):
    if generation != "":
        return "zinc22{}/{}/{}{}{}.{}".format(generation, hac, hac, logp, charge, format)
    else:
        return "{}/{}{}{}.{}".format(hac, hac, logp, charge, format)

def CurlDownloader(hac, logp, format, add_url, charge, generation):
    if generation != '':
        return "curl --remote-time --fail --create-dirs -o {hac}/{hac}{logp}{charge}.{format} {base_url}zinc22/zinc-22{generation}/{hac}/{hac}{logp}/". \
        format(hac=hac, logp=logp, format=format, base_url=base_url, add_url=add_url, charge=charge, generation=generation)
    else:
        return "curl  --user '{user}:{password}' --remote-time --fail --create-dirs -o {hac}/{hac}{logp}{charge}.{format} {base_url}{add_url}{hac}/{hac}{logp}{charge}.{format}". \
        format(hac=hac, logp=logp, format=format, base_url=base_url, add_url=add_url, charge=charge, user = Config.DOWNLOAD_USERNAME_2D, password = Config.DOWNLOAD_PASS_2D)


def WgetDownloader(hac, logp, format, add_url, charge, generation):
    if generation != '':
        return "wget -nH -r -l7 -np -A '*-{charge}-*{format}' {base_url}zinc22/zinc-22{generation}/{hac}/{hac}{logp}". \
        format(hac=hac, logp=logp, format=format, base_url=base_url, add_url=add_url, charge=charge, generation=generation)
    else:
        return "mkdir -pv {hac} && wget --user {user} --password {password} {base_url}{add_url}{hac}/{hac}{logp}{charge}.{format} -O {hac}/{hac}{logp}{charge}.{format}". \
        format(hac=hac, logp=logp, format=format, base_url=base_url, add_url=add_url, charge=charge, user = Config.DOWNLOAD_USERNAME_2D, password = Config.DOWNLOAD_PASS_2D)

def PowerShellDownloader(hac, logp, format, add_url, charge, generation):

    if generation != '':
        return "Invoke-WebRequest {base_url}zinc22/zinc-22{generation}/{hac}/{hac}{logp} " \
           "-OutFile (New-Item -Path \"{hac}/{logp}/{charge}/{hac}{logp}{charge}{generation}.{format}\" -Force )".format(hac=hac, logp=logp, format=format, base_url=base_url,
                                                                add_url_2D=add_url, charge=charge, generation=generation)
    else:
        return "Invoke-WebRequest {base_url}{add_url}{hac}/{hac}{logp}{charge}.{format} " \
           "-OutFile (New-Item -Path \"{hac}/{logp}/{hac}{logp}{charge}.{format}\" -Force )".format(hac=hac, logp=logp, format=format, base_url=base_url,
                                                                add_url_2D=add_url, charge=charge)
                                                
def RsyncDownloader(tranches, format):
    st = "mkdir zinc-22{generation} \npushd zinc-22{generation}\n".format(generation = tranches[0][0:1])
    
    for tranche in tranches:
        hac = tranche[1:4]
        logp = tranche[4:8]
        generation = tranche[0:1]
        charge = tranche[-1]
        st+= "rsync -Larv --include='*/' --include='zinc-22{generation}/{hac}/{hac}{logp}/[a-z]/' --include='[a-z]/{hac}{logp}-{charge}-*{format}' --exclude='*' --verbose rsync://files.docking.org/ZINC22-3D . \n". \
        format(hac=hac, logp=logp, format=format, base_url=base_url, charge=charge, generation=generation)
    st+= "popd"
    return st

URI_MIMETYPE_TO_FORMATTER = {
    'text/uri-list': URIFormatter,
    'text/bkslab': BKSLabFormatter,
    'text/aws': AWSFormatter,
    'text/oci': OCIFormatter,
    'text/wynton': WyntonFormatter,
    'text/x-ucsf-dock-database_index': DBFormatter,
    'application/x-ucsf-zinc-uri-downloadscript-curl': CurlDownloader,
    'application/x-ucsf-zinc-uri-downloadscript-wget': WgetDownloader,
    'application/x-ucsf-zinc-uri-downloadscript-powershell': PowerShellDownloader,
    'application/x-ucsf-zinc-uri-downloadscript-rsync': RsyncDownloader
}

URI_EXTENSION_TO_MIMETYPE = {
    'uri': 'text/uri-list',
    'bks': 'text/bkslab',
    'aws': 'text/aws',
    'oci': 'text/oci',
    'wynton': 'text/wynton',
    'database_index': 'text/x-ucsf-dock-database_index',
    'curl': 'application/x-ucsf-zinc-uri-downloadscript-curl',
    'wget': 'application/x-ucsf-zinc-uri-downloadscript-wget',
    'powershell': 'application/x-ucsf-zinc-uri-downloadscript-powershell',
    'rsync': 'application/x-ucsf-zinc-uri-downloadscript-rsync',
}

base_url = 'http://files.docking.org/'

axes = [('H04', 'H05', 'H06', 'H07', 'H08', 'H09', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15',
         'H16', 'H17',
         'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24', 'H25', 'H26', 'H27', 'H28', 'H29', 'H30', 'H31', 'H32', 'H33',
         'H34', 'H35', 'H36', 'H37', 'H38', 'H39', 'H40', 'H41', "H42", 'H43', 'H44', 'H45', 'H46', 'H47', 'H48', 'H49',
         'H50', 'H51', 'H52', 'H53', 'H54', 'H55', 'H56', 'H57', 'H58', 'H59', 'H60', 'H61'),
        ('M500', 'M400', 'M300', 'M200', 'M100', 'M000', 'P000', 'P010', 'P020', 'P030', 'P040', 'P050', 'P060', 'P070',
         'P080', 'P090', 'P100', 'P110', 'P120', 'P130', 'P140', 'P150', 'P160', 'P170', 'P180', 'P190', 'P200', 'P210',
         'P220',
         'P230', 'P240', 'P250', 'P260', 'P270', 'P280', 'P290', 'P300', 'P310', 'P320', 'P330', 'P340', 'P350', 'P360',
         'P370', 'P380', 'P390', 'P400', 'P410', 'P420', 'P430', 'P440', 'P450', 'P460', 'P470', 'P480', 'P490', 'P500',
         'P600',
         'P700', 'P800', 'P900'),
        ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
         'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F',
         'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
        ]
ticks = [(4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
          30, 31, 32, 33, 34, 35, 36, 37, 38),
         (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
          30, 31, 32, 33, 34, 35, 36, 37, 38)]

# H04-H49

full_axes = [[
            'H'+str(i).zfill(2) for i in range(4, 50)
        ] ,
            
        ('M500', 'M400', 'M300', 'M200', 'M100', 'M000', 'P000', 'P010', 'P020', 'P030', 'P040', 'P050', 'P060', 'P070',
         'P080', 'P090', 'P100', 'P110', 'P120', 'P130', 'P140', 'P150', 'P160', 'P170', 'P180', 'P190', 'P200', 'P210',
         'P220',
         'P230', 'P240', 'P250', 'P260', 'P270', 'P280', 'P290', 'P300', 'P310', 'P320', 'P330', 'P340', 'P350', 'P360',
         'P370', 'P380', 'P390', 'P400', 'P410', 'P420', 'P430', 'P440', 'P450', 'P460', 'P470', 'P480', 'P490', 'P500',
         'P600',
         'P700', 'P800', 'P900'),
        ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
         'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F',
         'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
        ]

#Format: 
#'subset-name': [[row-start, row-end], [col-start, col-end]]
subsets = {
        # 'all': [[0, 61], [0, 62]],
        # 'none': [[0, 0], [0, 0]],
        'shards': [[0, 33], [4, 10]],
        'fragments': [[0, 33], [7, 16]],
        'flagments': [[0, 43], [15, 20]],
        'lead-like': [[0, 43], [16, 25]],
        'goldilocks': [[20, 38], [18, 24]],
        'small-leads': [[0, 43], [16, 19]],
        'medium-leads': [[0, 43], [19, 22]],
        'big-leads': [[0, 43], [22, 25]],
        'lugs': [[0, 48], [23, 26]],
        'drug-like': [[0, 58], [0, 28]],
        'big-n-greasy': [[44, 500], [25, 30]]
}

charges = {
        "J": "J -4",
        "K": "K -3",
        "L": "L -2",
        "M": "M -1",
        "N": "N 0",
        "O": "O +1",
        "P": "P +2",
        "Q": "Q +3",
        "R": "R +4"
}

formats_3d = {
#    "SMILES" : "smi.tgz",
    "DOCK38" : "db2.tgz",
    "AutoDock" : "pdbqt.tgz",
    "Mol2" : "mol2.tgz",
    "SDF" : "sdf.tgz",
}

methods_3d ={
    "URIs" : "uri",
    "DOCK Database Index" : "database_index",
    "Wynton" : "wynton",
    "BKS Lab" : "bks",
    "AWS": "aws",
    "Oracle OCI": "oci",
    "WGET": "wget",
    "RSYNC": "rsync",
    "CURL": "curl",
    "PowerShell": "powershell"
}

methods_2d = {
    "URIs" : "uri",
    "DOCK Database Index" : "database_index",
    "WGET": "wget",
    "CURL": "curl",
    "PowerShell": "powershell"
}

formats_2d = {
    "SMILES" : "smi.gz",
    "Purchasing Information": "vendor.smi.gz",
#    "DOCK37" : "db2.tgz",
#    "AutoDock" : "pdbqt.tgz",
#    "Mol2" : "mol2.tgz",
#    "SDF" : "sdf.tgz",
}

generations = [chr(i) for i in range(97, 123)]

@app.route('/tranches/get2d', methods=['GET'])
def tranches2d():
    tranches = TrancheModel.query.filter_by(charge='-').all()
    cell2DNew = [[{} for x in range(62)] for y in range(61)]
    unfilteredSize = 0
    for i in tranches:
        row_idx = axes[0].index(str(i.h_num))
        col_idx = axes[1].index(str(i.p_num))
        if i.sum == 0:
            cell2DNew[col_idx][row_idx] = {'size': i.sum, 'chosen': False}
        else:
            cell2DNew[col_idx][row_idx] = {'size': i.sum, 'chosen': True}
        unfilteredSize += i.sum
    tranches = [i.to_dict() for i in tranches]
    return make_response({
        'tranches': tranches, 
        'cell2DNew': cell2DNew,
        'axes': full_axes, 
        'ticks': ticks, 
        'unfilteredSize': unfilteredSize, 
        'subsets': subsets,
        'formats': formats_2d,
        'methods': methods_2d
    }, 200)

@app.route('/tranches/get3d', methods=['GET'])
def tranches3d():
    tranches = TrancheModel.query.filter(TrancheModel.charge != '-').filter(TrancheModel.generation != '-').all()
    cell3DNew = [[{'tranches': [], 'size': 0, 'chosen': False} for x in range(62)] for y in range(61)]
    unfilteredSize = 0
    for i in tranches:
        row_idx = axes[0].index(str(i.h_num))
        col_idx = axes[1].index(str(i.p_num))
        if i.sum == 0:
            cell3DNew[col_idx][row_idx]['tranches'].append({'size': i.sum, 'chosen': False, 'charge': i.charge, 'generation': i.generation})
        else:
            cell3DNew[col_idx][row_idx]['tranches'].append({'size': i.sum, 'chosen': True, 'charge': i.charge, 'generation': i.generation})
        cell3DNew[col_idx][row_idx]['size'] += i.sum
        unfilteredSize += i.sum
    for i in cell3DNew:
        for j in i:
            if j['size'] != 0:
                j['chosen'] = True

    # return render_template('tranches/3D.html', tranches=tranches, axes=axes, cell3D=json.dumps(cell3DNew),
    #                        ticks=ticks, unfilteredSize=unfilteredSize)
    tranches = [i.to_dict() for i in tranches]
    
    return make_response({
        'tranches': tranches, 
        'axes': full_axes, 
        'cell3D': cell3DNew, 
        'ticks': ticks, 
        'unfilteredSize': unfilteredSize, 
        'charges': charges, 
        'subsets': subsets,
        'generations': generations,
        'formats': formats_3d,
        'methods': methods_3d
    }, 200)


@app.route('/tranches/2d/download', methods=['POST'])
def tranches2dDownload():
    formData = request.form
    data_ = formData['tranches'].split()
    format = formData['format']
    using = formData['method']
    mimetype = URI_EXTENSION_TO_MIMETYPE[using]
    if formData['format'] == 'vendor.smi.gz':
        add_url_2D = 'zinc22/vendors_zincid_map/current/'
        format = 'smi.gz'
    else:
        add_url_2D = 'zinc22/2d/'

    def gen_tranches(tranche):
        hac = tranche[0:3]
        logp = tranche[3:7]
        generation = ""
        return URI_MIMETYPE_TO_FORMATTER[mimetype](hac, logp, format, add_url_2D, '', generation)

    arr = map(gen_tranches, data_)
    data = '\n'.join(list(arr))
    if using == "PowerShell":
        download_filename = 'ZINC22-downloader-2D-{}.ps1'.format(format)    
    else:
        download_filename = 'ZINC22-downloader-2D-{}.{}'.format(format, using)
   
    return {
        'data': data,
        'filename': download_filename
    }, 200

zinc22_common_url = Config.SQLALCHEMY_BINDS["zinc22_common"]


def get3dfiles(tranches):
    #zinc22_common_url = Config.SQLALCHEMY_BINDS["zinc22_common"]
    #conn = psycopg2.connect(zinc22_common_url)
    
    zinc22_common_conn = psycopg2.connect(zinc22_common_url  )
    curs = zinc22_common_conn.cursor()
   
    # gen = tranches[0:1]
    # hac = tranches[1:4]
    # logp = tranches[4:8]
    # charge = tranches[-1]

    # curs.execute("select extra, suffix from holdings_3d_new where gen = '{}' and tranche = '{}' and charge = '{}'".format(gen, tranche, charge))
    # search by all instead
    curs.execute("drop table if exists temp_tranches")
    curs.execute("create temporary table if not exists temp_tranches (gen text, tranche text, charge text)")
    
    psql_query = "insert into temp_tranches (gen, tranche, charge) values "
    for i in tranches:
        psql_query += "('{}', '{}', '{}' ), ".format(i[0:1], i[1:8], i[-1])
    psql_query = psql_query[:-2]
    curs.execute(psql_query)
   
    psql_query = "select holdings_3d_new.extra, holdings_3d_new.suffix, temp_tranches.gen, temp_tranches.tranche, temp_tranches.charge from holdings_3d_new join temp_tranches on holdings_3d_new.gen = temp_tranches.gen and holdings_3d_new.tranche = temp_tranches.tranche and holdings_3d_new.charge = temp_tranches.charge"
    curs.execute(psql_query)

    file_results = []
 
    for r in curs.fetchall():
            
        extra  = r[0]
        suffix = r[1]
        gen = r[2]
        tranche = r[3]
        charge = r[4]
        logp = tranche[4:8]
        hac = tranche[1:4]

        file_results.append((extra, suffix, gen, tranche, charge, logp, hac))
    return file_results


@app.route('/tranches/3d/download', methods=['POST'])
def tranches3dDownload():
    formData = request.form
    tranches_data = formData['tranches'].split(" ")
    tranches_data = [i for i in tranches_data if i != '']
    
    dformat = formData['format']
    using = formData['method']
    mimetype = URI_EXTENSION_TO_MIMETYPE[using]
    add_url_3D = 'zinc22/3d/'

    dformat = dformat.strip()

    tranches_data = sorted(tranches_data)
    def gen_all_tranches(tranches):
        to_look_up = {}
        res = []
        for tranche in tranches:
            generation = tranche[0:1]
            hac = tranche[1:4]
            logp = tranche[4:8]
            charge = tranche[-1]
            prefix = URI_MIMETYPE_TO_FORMATTER[mimetype](hac, logp, dformat, add_url_3D, charge, generation)
            to_look_up[tranche] = prefix   
            
        db_res = get3dfiles(tranches)
        for extra, suffix, gen, tranche, charge, logp, hac in db_res:
            suffix = suffix.strip()
            extra = extra.strip()
            hac = hac.strip()
            logp = logp.strip()
            charge = charge.strip()
            generation = gen.strip()
            tranche = tranche.strip()
            prefix = to_look_up[generation+ tranche + charge]
            
            if mimetype != 'application/x-ucsf-zinc-uri-downloadscript-powershell':
                res.append(prefix + f"/{extra}/H{hac}{logp}-{charge}-{suffix}.{dformat}\n")
            else:
                res.append(prefix + "\n")
        
        return res
    
    def gen_all_rsyncs(tranches):
        return RsyncDownloader(tranches, dformat) + '\n'

 
    if mimetype == 'application/x-ucsf-zinc-uri-downloadscript-rsync':
        tranches_iter = gen_all_rsyncs(tranches_data)
    else:
        tranches_iter = gen_all_tranches(tranches_data)

    download_filename = 'ZINC22-downloader-3D-{}.{}'.format(dformat, using)
    
    return {
        'data': "".join(tranches_iter),
        'filename': download_filename
    }, 200



  
