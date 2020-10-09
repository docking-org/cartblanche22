from flask import render_template
from app.main import application
from app.data.models.tranche import Tranche
import json

@application.route('/tranches', methods=['GET'])
def tranches():
    tranches = Tranche.query.order_by(Tranche.h_num, Tranche.p_num).all()
    axes = [('H00', 'H01', 'H02', 'H03', 'H04', 'H05', 'H06', 'H07', 'H08', 'H09', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15',
     'H16', 'H17',
          'H18','H19', 'H20', 'H21', 'H22', 'H23', 'H24', 'H25', 'H26', 'H27', 'H28', 'H29', 'H30', 'H31', 'H32', 'H33',
          'H34','H35',  'H36', 'H37', 'H38', 'H39', 'H40', 'H41', "H42", 'H43', 'H44', 'H45', 'H46', 'H47', 'H48', 'H49',
          'H50', 'H51', 'H52', 'H53', 'H54', 'H55', 'H56', 'H57', 'H58', 'H59', 'H60', None),
         ('M500','M400','M300', 'M200','M100','M000','P000', 'P010', 'P020', 'P030', 'P040', 'P050', 'P060', 'P070',
          'P080','P090', 'P100', 'P110', 'P120', 'P130','P140','P150','P160','P170','P180','P190','P200', 'P210', 'P220',
          'P230', 'P240', 'P250', 'P260', 'P270', 'P280', 'P290', 'P300', 'P310', 'P320', 'P330', 'P340', 'P350', 'P360',
          'P370','P380','P390','P400','P410','P420', 'P430','P440', 'P450','P460', 'P470','P480','P490','P500','P600',
          'P700', 'P800', 'P900', None)]
    ticks = [ (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
         30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
         58, 59, 60),]
    cell2D = [[0 for x in range(62)] for y in range(62)]
    unfilteredSize = 0
    for i in tranches:
        if i.mwt.isnumeric():
            col_idx = i.mwt
        elif i.mwt.isupper():
            col_idx = ord(i.mwt) - 29
        else:
            col_idx = ord(i.mwt) - 87
        if i.logp.isnumeric():
            row_idx = i.logp
        elif i.logp.isupper():
            row_idx = ord(i.logp) - 29
        else:
            row_idx = ord(i.logp) - 87
        cell2D[int(col_idx)][int(row_idx)] = i.sum
        unfilteredSize += i.sum
    return render_template('tranches/home.html', tranches = tranches, axes = axes, cell2D=json.dumps(cell2D),
                           ticks=ticks, unfilteredSize=unfilteredSize)