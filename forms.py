# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Regexp

class AddWinningNumberForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    numbers = StringField('Winning Numbers', validators=[
        DataRequired(),
        Regexp(r'^(\d{1,2},){4}\d{1,2}$', message="Enter five numbers separated by commas.")
    ])
    submit = SubmitField('Add')

class EditRecordForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    numbers = StringField('Winning Numbers', validators=[
        DataRequired(),
        Regexp(r'^(\d{1,2},){4}\d{1,2}$', message="Enter five numbers separated by commas.")
    ])
    submit = SubmitField('Update')
