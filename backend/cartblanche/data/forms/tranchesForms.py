from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField

from wtforms.validators import DataRequired, Optional

DOWNLOAD_USING_LABELS = {
    'uri': 'URLs',
    'database_index': 'DOCK (Split) Database Index',
    'curl': 'Download Script (curl)',
    'wget': 'Download Script (wget)',
    'powershell': 'Download Script (powershell)',
}

URI_EXTENSION_TO_MIMETYPE = {
    'uri': 'text/uri-list',
    'database_index': 'text/x-ucsf-dock-database_index',
    'curl': 'application/x-ucsf-zinc-uri-downloadscript-curl',
    'wget': 'application/x-ucsf-zinc-uri-downloadscript-wget',
    'powershell': 'application/x-ucsf-zinc-uri-downloadscript-powershell',
}


class Tranche2DFileFactory():
    AVAILABLE_FORMATS = [
        ('txt', 'TXT'),
        ('smi.gz', 'SMILES'),
    ]

    @property
    def txt(self):
        return self.get_format('txt')

    @property
    def smiles(self):
        return self.get_format('smi.gz')


class Tranche3DFileFactory():
    AVAILABLE_FORMATS = [
        ('smi.tgz', 'SMILES'),
        ('db.tgz', 'DB'),
        ('db2.tgz', 'DB2'),
        ('mol2.tgz', 'Mol2'),
        ('pdbqt.tgz', 'PDBQT'),
        ('sdf.tgz', 'SDF'),
    ]

    def get_list(self, format):
        return self.get_chunked_format(format)

    @property
    def smi(self):
        return self.get_list('smi.gz')

    @property
    def db(self):
        return self.get_list('db.gz')

    @property
    def db2(self):
        return self.get_list('db2.gz')

    @property
    def mol2(self):
        return self.get_list('mol2.tgz')

    @property
    def solvation(self):
        return self.get_format('solv')

    @property
    def pdbqt(self):
        return self.get_format('pdbqt.gz')

    @property
    def sdf(self):
        return self.get_format('sdf.gz')


class Download2DForm(FlaskForm):
    tranches = TextAreaField('tranches',
                             validators=[DataRequired()],
                             default='')
    format = SelectField('format',
                         choices=(Tranche2DFileFactory.AVAILABLE_FORMATS),
                         validators=[DataRequired()],
                         default='txt')
    using = SelectField('using',
                        choices=[(key, DOWNLOAD_USING_LABELS[key]) for key, _ in URI_EXTENSION_TO_MIMETYPE.items()],
                        validators=[Optional()],
                        default='uri')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('csrf_enabled', False)
        super(Download2DForm, self).__init__(*args, **kwargs)


class Download3DForm(FlaskForm):
    tranches = TextAreaField('tranches',
                             validators=[DataRequired()],
                             default='')
    format = SelectField('format',
                         choices=(Tranche3DFileFactory.AVAILABLE_FORMATS),
                         validators=[DataRequired()],
                         default='txt')
    using = SelectField('using',
                        choices=[(key, DOWNLOAD_USING_LABELS[key]) for key, _ in URI_EXTENSION_TO_MIMETYPE.items()],
                        validators=[Optional()],
                        default='uri')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('csrf_enabled', False)
        super(Download3DForm, self).__init__(*args, **kwargs)