from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional

class formEditDojo(FlaskForm):
    name = StringField(label='Dojo Name', validators=[DataRequired()])
    location = StringField(label='Dojo Location', validators=[DataRequired()])
    instructor_membership = SelectField(
        label='Instructor', choices='', validators=[DataRequired()])
    submit = SubmitField(label='Save Changes')

class formConfirmAction(FlaskForm):
    submit = SubmitField(label='Proceed')