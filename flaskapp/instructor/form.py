from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional
import datetime


class formEditInstructor(FlaskForm):
    membership = StringField(label='Membership ID', validators=[validators.Optional()])
    dateOfBirth_month = SelectField(validators=[validators.Optional()],choices=[i for i in range(1,13)])
    currentyear = int(datetime.date.today().year)
    dateOfBirth_year = SelectField(validators=[validators.Optional()],choices=[i for i in range(currentyear,currentyear-100,-1)])
    firstName = StringField(label='Name', validators=[DataRequired()])
    lastName = StringField(label='Surname', validators=[DataRequired()])
    belt_id = SelectField(label='Belt', choices='', validators=[DataRequired()])
    lastGrading = DateField(label='Last Grading Date', validators=[validators.Optional()])
    submit = SubmitField(label='Save Changes')


class formSearchStudent(FlaskForm):
    name = StringField(label='Name', validators=[validators.Optional()])
    belt = SelectField(label='Belt', choices=[("","")],validators=[validators.Optional()])
    submit = SubmitField(label='Search')
