from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional
from flaskapp.instructor.helpers import belt_type

class formEditInstructor(FlaskForm):
    firstName = StringField(label='Name without Surname', validators=[DataRequired()])
    lastName = StringField(label='surname', validators=[DataRequired()])
    belt = SelectField(label='Belt', choices=belt_type(),validators=[DataRequired()])
    lastGrading = DateField(label='Last Grading Date',
                            validators=[validators.Optional()])
    submit = SubmitField(label='Save Changes')

class formSearchStudent(FlaskForm):
    name = StringField(label='Name', validators=[validators.Optional()])
    belt = SelectField(label='Belt', choices=[("","")]+belt_type(),validators=[validators.Optional()])
    submit = SubmitField(label='Search')
