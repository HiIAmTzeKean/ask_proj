from flask_wtf import FlaskForm
from wtforms import StringField, validators, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Optional
import datetime


class formStudentIdentifier(FlaskForm):
    membership = StringField(label='Membership ID', validators=[DataRequired()])
    dateOfBirth_month = SelectField(validators=[validators.Optional()],choices=[i for i in range(1,13)])
    currentyear = int(datetime.date.today().year)
    dateOfBirth_year = SelectField(validators=[validators.Optional()],choices=[i for i in range(currentyear,currentyear-100,-1)])
    submit = SubmitField(label='Submit')