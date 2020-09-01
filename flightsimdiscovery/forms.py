from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flightsimdiscovery.models import User
from utilities import validate_lat, validate_long, get_country_list, get_category_list

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):

    
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PoiCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    country = SelectField('Country', choices = get_country_list(), validators=[DataRequired()])
    category = SelectField('Category', choices = get_category_list(), validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    latitude = StringField('Latitude (decimal degrees)', validators=[DataRequired(), Length(min=2, max=18)])
    longitude = StringField('Longitude (decimal degrees)', validators=[DataRequired(), Length(min=2, max=18)])
    nearest_airport = StringField('Nearest Airpot (ICAO)', validators=[Length(min=0, max=4)])
    # remember = BooleanField('Remember Me')
    submit = SubmitField('Create')

    def validate_latitude(self, latitude):

        # add logic here
        if not validate_lat(str(latitude.data)):
            raise ValidationError('Please enter a valid latitude (-90 and +90) in degrees decimal.  e.g.-34.407279')

    def validate_longitude(self, longitude):

        if not validate_long(str(longitude.data)):
            raise ValidationError('Please enter a valid longitude (-180 and +180) in degrees decimal   e.g. 150.676888')

class PoiUpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    country = SelectField('Country', choices = get_country_list(), validators=[DataRequired()])
    category = SelectField('Category', choices = get_category_list(), validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    latitude = StringField('Latitude (decimal degrees) ', validators=[DataRequired(), Length(min=2, max=18)])
    longitude = StringField('Longitude (decimal degrees)', validators=[DataRequired(), Length(min=2, max=18)])
    nearest_airport = StringField('Nearest Airpot (ICAO)', validators=[Length(min=0, max=4)])
    # remember = BooleanField('Remember Me')
    submit = SubmitField('Update')

    def validate_latitude(self, latitude):

        # add logic here
        if not validate_lat(str(latitude.data)):
            raise ValidationError('Please enter a valid latitude (-90 and +90) in degrees decimal.  e.g.-34.407279')

    def validate_longitude(self, longitude):

        if not validate_long(str(longitude.data)):
            raise ValidationError('Please enter a valid longitude (-180 and +180) in degrees decimal   e.g. 150.676888')