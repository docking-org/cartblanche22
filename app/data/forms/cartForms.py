from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.data.models.users import Users
from app.data.models.carts import Carts

class CartForm(FlaskForm):
    name = StringField('Cart name', validators=[DataRequired()])
    submit = SubmitField('Save')