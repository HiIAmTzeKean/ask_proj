from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional
import datetime


class formDojoSelection(FlaskForm):
    dojoName = SelectField(label='Dojo Name', choices='',
                           validators=[DataRequired()])
    submit = SubmitField('Submit')


class formAdd_DelStudent(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    belt = StringField(label='Belt', validators=[DataRequired()])
    submit = SubmitField('Submit')


class formEditStudent(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    belt = StringField(label='Belt', validators=[DataRequired()])
    lastGrading = DateField(label='lastGrading', validators=[validators.Optional()])
    dojo_id = SelectField(label='Dojo Name', choices='',validators=[DataRequired()])
    submit = SubmitField(label='Save')


class formGradePerformance(FlaskForm):
    formChoice = [(1, '1'),(2, '2'),(3, '3'),(4, '4'),(5, '5'),]
    Technique = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()])
    Ukemi = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()])
    Discipline = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()])
    Coordination = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()])
    Knowledge = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()])
    Spirit = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()])
