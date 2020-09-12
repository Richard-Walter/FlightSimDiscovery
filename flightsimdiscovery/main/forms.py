from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError

class ContactForm(FlaskForm):

    message = TextAreaField('Enter Message', validators=[DataRequired()])
    subject = StringField('Enter Subject', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')