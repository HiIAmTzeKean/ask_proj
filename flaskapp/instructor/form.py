from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional
from flaskapp.attendance.helpers import belt_type
import datetime

class formEditInstructor(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    belt = SelectField(label='Belt', choices=belt_type(),validators=[DataRequired()])
    lastGrading = DateField(label='Last Grading Date',
                            validators=[validators.Optional()])
    submit = SubmitField(label='Save Changes')