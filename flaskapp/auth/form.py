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


from flask_security.forms import ConfirmRegisterForm
from flaskapp.models import Student
from wtforms.validators import ValidationError
class ExtendedRegisterForm(ConfirmRegisterForm):
    membership_id = StringField('Membership ID', [DataRequired()])

    def validate_membership_id(self, field):

        # extract the membership data give
        membership = field.data

        # check against database
        registred_student = Student.query.filter_by(membership=membership).first()
        if registred_student is None:
            # the "student" is not registered thus not authorized 
            # then the given "email" is not validated
            raise ValidationError('Membership ID does not exit, please contact HQ')