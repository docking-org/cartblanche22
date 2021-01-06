from flask import render_template, request, Response
from app.main import application
import json
from app.data.models.tranche import TrancheModel
from app.data.forms.tranchesForms import DownloadForm


def URIFormatter(hac, logp, format):
    return "{}{}/{}{}.{}".format(base_url, hac, hac, logp, format)


def DBFormatter(hac, logp, format):
    return "{}/{}{}.{}".format(hac, hac, logp, format)


def CurlDownloader(hac, logp, format):
    return "curl --remote-time --fail --create-dirs -o {hac}/{hac}{logp}.{format} {base_url}{hac}/{hac}{logp}.{format}". \
        format(hac=hac, logp=logp, format=format, base_url=base_url)


def WgetDownloader(hac, logp, format):
    return "mkdir -pv {hac} && wget {base_url}{hac}/{hac}{logp}.{format} -O {hac}/{hac}{logp}.{format}". \
        format(hac=hac, logp=logp, format=format, base_url=base_url)


def PowerShellDownloader(hac, logp, format):
    return "New-Item -path {hac} -type directory; Invoke-WebRequest {base_url}{hac}/{hac}{logp}.{format} " \
           "-OutFile {hac}/{hac}{logp}.{format}".format(hac=hac, logp=logp, format=format, base_url=base_url)


URI_MIMETYPE_TO_FORMATTER = {
    'text/uri-list': URIFormatter,
    'text/x-ucsf-dock-database_index': DBFormatter,
    'application/x-ucsf-zinc-uri-downloadscript-curl': CurlDownloader,
    'application/x-ucsf-zinc-uri-downloadscript-wget': WgetDownloader,
    'application/x-ucsf-zinc-uri-downloadscript-powershell': PowerShellDownloader
}

URI_EXTENSION_TO_MIMETYPE = {
    'uri': 'text/uri-list',
    'database_index': 'text/x-ucsf-dock-database_index',
    'curl': 'application/x-ucsf-zinc-uri-downloadscript-curl',
    'wget': 'application/x-ucsf-zinc-uri-downloadscript-wget',
    'powershell': 'application/x-ucsf-zinc-uri-downloadscript-powershell',
}

base_url = 'http://files.docking.org/zinc22/2d/'

axes = [('H00', 'H01', 'H02', 'H03', 'H04', 'H05', 'H06', 'H07', 'H08', 'H09', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15',
         'H16', 'H17',
         'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24', 'H25', 'H26', 'H27', 'H28', 'H29', 'H30', 'H31', 'H32', 'H33',
         'H34', 'H35', 'H36', 'H37', 'H38', 'H39', 'H40', 'H41', "H42", 'H43', 'H44', 'H45', 'H46', 'H47', 'H48', 'H49',
         'H50', 'H51', 'H52', 'H53', 'H54', 'H55', 'H56', 'H57', 'H58', 'H59', 'H60', 'H61', None),
        ('M500', 'M400', 'M300', 'M200', 'M100', 'M000', 'P000', 'P010', 'P020', 'P030', 'P040', 'P050', 'P060', 'P070',
         'P080', 'P090', 'P100', 'P110', 'P120', 'P130', 'P140', 'P150', 'P160', 'P170', 'P180', 'P190', 'P200', 'P210',
         'P220',
         'P230', 'P240', 'P250', 'P260', 'P270', 'P280', 'P290', 'P300', 'P310', 'P320', 'P330', 'P340', 'P350', 'P360',
         'P370', 'P380', 'P390', 'P400', 'P410', 'P420', 'P430', 'P440', 'P450', 'P460', 'P470', 'P480', 'P490', 'P500',
         'P600',
         'P700', 'P800', 'P900', None),
        ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
         'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F',
         'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', None)
        ]
ticks = [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
          30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
          57,
          58, 59, 60, 61),
         (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
          30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
          57,
          58, 59, 60)]


@application.route('/tranches/2d', methods=['GET'])
def tranches2d():
    form = DownloadForm()
    tranches = TrancheModel.query.filter_by(charge='-').all()
    cell2D = [[0 for x in range(62)] for y in range(62)]
    cell2DNew = [[{} for x in range(62)] for y in range(61)]
    unfilteredSize = 0
    for i in tranches:
        row_idx = axes[0].index(str(i.h_num))
        col_idx = axes[1].index(str(i.p_num))
        if i.sum == 0:
            cell2DNew[col_idx][row_idx] = {'size': i.sum, 'chosen': False}
        else:
            cell2DNew[col_idx][row_idx] = {'size': i.sum, 'chosen': True}
        cell2D[col_idx][row_idx] = i.sum
        unfilteredSize += i.sum
    # print(cell2DNew)
    return render_template('tranches/homeNew.html', tranches=tranches, axes=axes, cell2D=json.dumps(cell2D),
                           cell2DNew=json.dumps(cell2DNew),
                           ticks=ticks, unfilteredSize=unfilteredSize, form=form)


@application.route('/tranches/3d', methods=['GET'])
def tranches3d():
    tranches = TrancheModel.query.filter(TrancheModel.charge != '-').all()
    cell3DNew = [[{'tranches': [], 'size': 0, 'chosen': False} for x in range(62)] for y in range(61)]
    unfilteredSize = 0
    for i in tranches:
        row_idx = axes[0].index(str(i.h_num))
        col_idx = axes[1].index(str(i.p_num))
        if i.sum == 0:
            cell3DNew[col_idx][row_idx]['tranches'].append({'size': i.sum, 'chosen': False, 'charge': i.charge})
        else:
            cell3DNew[col_idx][row_idx]['tranches'].append({'size': i.sum, 'chosen': True, 'charge': i.charge})
        cell3DNew[col_idx][row_idx]['size'] += i.sum
        unfilteredSize += i.sum
    for i in cell3DNew:
        for j in i:
            if j['size'] != 0:
                j['chosen'] = True

    return render_template('tranches/3D.html', tranches=tranches, axes=axes, cell3D=json.dumps(cell3DNew),
                           ticks=ticks, unfilteredSize=unfilteredSize)


@application.route('/tranches/2d/download', methods=['POST'])
def tranches2dDownload():
    formData = DownloadForm(request.values)
    data_ = formData.tranches.data.split()
    format = formData.format.data
    using = formData.using.data
    mimetype = URI_EXTENSION_TO_MIMETYPE[using]

    def gen_tranches(tranche):
        hac = tranche[0:3]
        logp = tranche[3:7]
        return URI_MIMETYPE_TO_FORMATTER[mimetype](hac, logp, format)

    arr = map(gen_tranches, data_)
    data = '\n'.join(list(arr))
    download_filename = 'ZINC22-downloader-2D-{}.{}'.format(format, using)
    response = Response(data, mimetype=mimetype)
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(download_filename)
    return response
