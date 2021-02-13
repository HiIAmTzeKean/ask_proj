from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, Optional
import datetime


class gradePerformanceform(FlaskForm):
    lesson_id = SelectField(label='Last Lesson', choices='',validators=[DataRequired()])
    formChoice = [(i, str(i)) for i in range(1,11)]
    technique = SelectField(label='Technique', choices=formChoice,validators=[DataRequired()], default=5)
    ukemi = SelectField(label='Ukemi', choices=formChoice,validators=[DataRequired()], default=5)
    discipline = SelectField(label='discipline', choices=formChoice,validators=[DataRequired()], default=5)
    coordination = SelectField(label='coordination', choices=formChoice,validators=[DataRequired()], default=5)
    knowledge = SelectField(label='knowledge', choices=formChoice,validators=[DataRequired()], default=5)
    spirit = SelectField(label='spirit', choices=formChoice,validators=[DataRequired()], default=5)
    submit = SubmitField('Submit')