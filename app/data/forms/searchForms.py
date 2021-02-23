from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class SearchSmilesForm(FlaskForm):
    list_of_smiles = TextAreaField(validators=[])
    smiles_file = FileField('Text File', validators=[])
    dist = SelectField('dist',
                         choices=(
                             ('0', '0'),
                             ('1', '1'),
                             ('2', '2'),
                         ),
                         validators=[DataRequired()],
                         default='0')
    submit = SubmitField('Search')


class SearchZincForm(FlaskForm):
    zinc_id = StringField('Enter single zinc id', validators=[])
    list_of_zinc_id = TextAreaField('Enter multiple zinc ids with new line', validators=[])
    zinc_file = FileField('Text File', validators=[])
    submit = SubmitField('Search')


class SearchSupplierForm(FlaskForm):
    list_of_suppliercode = TextAreaField(validators=[])
    supplier_file = FileField('Text File', validators=[])
    submit = SubmitField('Search')


class SearchRandom(FlaskForm):
    kind = SelectField('kind',
                         choices=(
                             ('zincid', 'ZINCID'),
                             ('smiles', 'SMILES'),
                         ),
                         validators=[DataRequired()],
                         default='zincid')

    amount = SelectField('amount',
                         choices=(
                             ('100', '100'),
                             ('500', '500'),
                             ('1000', '1000'),
                         ),
                         validators=[DataRequired()],
                         default='100')

    format = SelectField('format',
                         choices=(
                             ('txt', 'TXT'),
                         ),
                         validators=[DataRequired()],
                         default='txt')
    submit = SubmitField('Download')