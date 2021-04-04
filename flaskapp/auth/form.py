from flask_wtf import FlaskForm
from wtforms import (BooleanField, FieldList, FormField, IntegerField,
                     PasswordField, SelectField, StringField, SubmitField,
                     validators)
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired


class formRegister(FlaskForm):
    firstName = StringField(label='Name', validators=[DataRequired()])
    lastName = StringField(label='Surname', validators=[DataRequired()])
    email = StringField(label='Email', validators=[Email(message='Invalid email address')])
    password = PasswordField(label='Password', validators=[DataRequired()])
    passwordConfirm = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField(label='Register')


class formLogin(FlaskForm):
    email = StringField(label='Email', validators=[Email(message='Invalid email address')])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


from flask_security.forms import RegisterForm

class ExtendedRegisterForm(RegisterForm):
    firstName = StringField('First Name', [DataRequired()])
    lastName = StringField('Last Name', [DataRequired()])