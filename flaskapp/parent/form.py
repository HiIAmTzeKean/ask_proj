from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, SelectField, FieldList, FormField, RadioField, TextAreaField
from wtforms.widgets import TextArea
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional
import datetime


class formStudentIdentifier(FlaskForm):
    membership = StringField(label='Membership ID', validators=[DataRequired()])
    dateOfBirth_month = SelectField(validators=[validators.Optional()], choices=[''] + [i for i in range(1,13)])
    currentyear = int(datetime.date.today().year)
    dateOfBirth_year = SelectField(validators=[validators.Optional()],choices=[''] + [i for i in range(currentyear,currentyear-100,-1)])
    submit = SubmitField(label='Submit')


class formQuestion(FlaskForm):
    question = SelectField(choices=[i for i in range(1,11)], default=1)


class formQuestions(FlaskForm):
    membership = StringField(label='Membership ID', validators=[DataRequired()])
    dateOfBirth_month = SelectField(validators=[validators.DataRequired()], choices=[''] + [i for i in range(1,13)])
    currentyear = int(datetime.date.today().year)
    dateOfBirth_year = SelectField(validators=[validators.DataRequired()],choices=[''] + [i for i in range(currentyear,currentyear-100,-1)])
    date = DateField(label='Date', default=datetime.date.today(), validators=[DataRequired()])

    # multiple QN using field list
    questions = FieldList(RadioField(choices=[i for i in range(1,11)], default=1))
    comments = TextAreaField(label='Comments', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField(label='Submit')
