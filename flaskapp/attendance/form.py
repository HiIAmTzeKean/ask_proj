from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional

class formDojoSelection(FlaskForm):
    dojoName = SelectField(label='Dojo Name', choices='',validators=[DataRequired()])
    submit = SubmitField('Submit')

class formAdd_DelStudent(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    belt = StringField(label='Belt', validators=[DataRequired()])
    lastGrading = DateField(label='lastGrading', default=None)
    submit = SubmitField('Submit')