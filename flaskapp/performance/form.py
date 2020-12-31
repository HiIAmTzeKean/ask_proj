from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional
import datetime


class formGradePerformance(FlaskForm):
    formChoice = [(1, '1'),(2, '2'),(3, '3'),(4, '4'),(5, '5'),]
    technique = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()])
    ukemi = SelectField(label='Ukemi', choices=formChoice,validators=[DataRequired()])
    discipline = SelectField(label='discipline', choices=formChoice,validators=[DataRequired()])
    coordination = SelectField(label='coordination', choices=formChoice,validators=[DataRequired()])
    knowledge = SelectField(label='knowledge', choices=formChoice,validators=[DataRequired()])
    spirit = SelectField(label='spirit', choices=formChoice,validators=[DataRequired()])
    submit = SubmitField('Submit')