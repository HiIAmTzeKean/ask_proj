from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional
from flaskapp.attendance.helpers import belt_type
import datetime


class formDojoSelection(FlaskForm):
    dojo_id = SelectField(label='Dojo Name', choices='', validators=[DataRequired()])
    submit = SubmitField('Submit')


class formAdd_DelStudent(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    # belt = StringField(label='Belt', validators=[DataRequired()])
    belt = SelectField(label='Belt', choices=belt_type(), validators=[DataRequired()])
    lastGrading = DateField(label='Last Grading Date', validators=[validators.Optional()])
    dojo_id = SelectField(label='Dojo Name', choices='', validators=[DataRequired()])
    submit = SubmitField('Add student')


class formEditStudent(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    belt = SelectField(label='Belt', choices=belt_type(),validators=[DataRequired()])
    lastGrading = DateField(label='Last Grading Date',
                            validators=[validators.Optional()])
    submit = SubmitField(label='Save Changes')


class formSearchStudent(FlaskForm):
    name = StringField(label='Name', validators=[validators.Optional()])
    belt = SelectField(label='Belt', choices=[("","")]+belt_type(),validators=[validators.Optional()])
    submit = SubmitField(label='Search')


class formEditDojo(FlaskForm):
    name = StringField(label='Dojo Name', validators=[DataRequired()])
    location = StringField(label='Dojo Location', validators=[DataRequired()])
    instructor_id = SelectField(
        label='Instructor', choices='', validators=[DataRequired()])
    submit = SubmitField(label='Save Changes')


class formStartLesson(FlaskForm):
    instructor_id = SelectField(
        label='Instructor Name', choices='', validators=[DataRequired()])
    date = DateField(label='Lesson Date',
                     default=datetime.date.today(), validators=[DataRequired()])
    submit = SubmitField('Start Lesson')
