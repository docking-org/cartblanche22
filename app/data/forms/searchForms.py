from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, validators, TextAreaField
from wtforms.validators import DataRequired

class searchFileForm(FlaskForm):
    file = FileField('Text File', validators=[DataRequired()])
    submit = SubmitField('Search')

class searchZincForm(FlaskForm):
    id = StringField('Enter single zinc id', validators=[DataRequired()])
    submit = SubmitField('Search')

class searchZincListForm(FlaskForm):
    listData = TextAreaField('Enter multiple zinc ids with new line', validators=[DataRequired()])
    submit = SubmitField('Search')
