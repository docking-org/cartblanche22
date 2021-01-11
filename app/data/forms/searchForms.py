from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, TextAreaField


class SearchSmilesForm(FlaskForm):
    list_of_smiles = TextAreaField(validators=[])
    smiles_file = FileField('Text File', validators=[])
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
