from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from utilities import validate_lat, validate_long, get_country_list, get_category_list
from flightsimdiscovery.pois.utils import validate_poi_name


class PoiCreateForm(FlaskForm):
   
    name = StringField('Name', validators=[DataRequired()])
    country = SelectField('Country', choices=get_country_list(), validators=[DataRequired()])
    category = SelectField('Category', choices=get_category_list(), validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    latitude = StringField('Latitude (decimal degrees)', validators=[DataRequired(), Length(min=2, max=18)])
    longitude = StringField('Longitude (decimal degrees)', validators=[DataRequired(), Length(min=2, max=18)])
    nearest_airport = StringField('Nearest Airpot (ICAO)', validators=[Length(min=0, max=4)])
    share = BooleanField('Share with the community', default="checked")
    submit = SubmitField('Create')

    def validate_latitude(self, latitude):

        if not validate_lat(str(latitude.data)):
            raise ValidationError('Please enter a valid latitude (-90 and +90) in degrees decimal.  e.g.-34.407279')

    def validate_longitude(self, longitude):

        if not validate_long(str(longitude.data)):
            raise ValidationError('Please enter a valid longitude (-180 and +180) in degrees decimal   e.g. 150.676888')

    def validate_name(self, name):

        if not validate_poi_name(name.data):
            raise ValidationError('This name is already used by another point of interest')

class PoiUpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    country = SelectField('Country', choices=get_country_list(), validators=[DataRequired()])
    category = SelectField('Category', choices=get_category_list(), validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    latitude = StringField('Latitude (decimal degrees) ', validators=[DataRequired(), Length(min=2, max=18)])
    longitude = StringField('Longitude (decimal degrees)', validators=[DataRequired(), Length(min=2, max=18)])
    nearest_airport = StringField('Nearest Airpot (ICAO)', validators=[Length(min=0, max=4)])
    share = BooleanField('Share with the community')
    submit = SubmitField('Update')

    def validate_latitude(self, latitude):

        if not validate_lat(str(latitude.data)):
            raise ValidationError('Please enter a valid latitude (-90 and +90) in degrees decimal.  e.g.-34.407279')

    def validate_longitude(self, longitude):

        if not validate_long(str(longitude.data)):
            raise ValidationError('Please enter a valid longitude (-180 and +180) in degrees decimal   e.g. 150.676888')
        
    def validate_name(self, name):

        if not validate_poi_name(name.data):
            raise ValidationError('This name is already used by another point of interest')

