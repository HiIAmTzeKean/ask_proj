from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class formMembership(FlaskForm):
    membership = StringField(label='Membership', validators=[DataRequired()])
    submit = SubmitField('Submit')