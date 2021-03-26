from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField
from wtforms.validators import DataRequired
import datetime


class formStudentIdentifier(FlaskForm):
    membership = StringField(label='Membership ID', validators=[DataRequired()])
    submit = SubmitField(label='Submit')