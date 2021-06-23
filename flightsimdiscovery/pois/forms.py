from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError
from utilities import validate_lat, validate_long, get_country_list, get_category_list, get_new_poi_category_list
from flightsimdiscovery.pois.utils import validate_poi_name


class PoiCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    country = SelectField('Country', choices=get_country_list(), render_kw={'disabled': False}, validators=[DataRequired()])
    category = SelectField('Category', choices=get_new_poi_category_list(), validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    latitude = StringField('Latitude (decimal degrees) e.g. -34.407279', validators=[DataRequired(), Length(min=2, max=18)])
    longitude = StringField('Longitude (decimal degrees) e.g. 150.676888', validators=[DataRequired(), Length(min=2, max=18)])
    nearest_airport = StringField('Nearest Airpot (ICAO) (optional) e.g. KLAX', validators=[Length(min=0, max=4)])
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
    poi_name = HiddenField("Name")
    name = StringField('Name', validators=[DataRequired()])
    country = SelectField('Country', choices=get_country_list(), render_kw={'disabled': False}, validators=[DataRequired()])
    # country = StringField('Country', render_kw={'disabled': False})
    category = SelectField('Category', choices=get_new_poi_category_list(), validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    latitude = StringField('Latitude (decimal degrees) ', render_kw={'disabled': False}, validators=[DataRequired(), Length(min=2, max=18)])
    # latitude = StringField('Latitude (decimal degrees) ', render_kw={'disabled': False})
    longitude = StringField('Longitude (decimal degrees)',render_kw={'disabled': False},  validators=[DataRequired(), Length(min=2, max=18)])
    altitude = StringField('altitude (meter)',render_kw={'disabled': False},  validators=[Length(min=1, max=6)])
    # longitude = StringField('Longitude (decimal degrees)',render_kw={'disabled': False})
    # nearest_airport = StringField('Nearest Airpot (ICAO) (optional)', validators=[Length(min=0, max=4)])
    share = BooleanField('Share with the community')
    submit = SubmitField('Update')

    def validate_latitude(self, latitude):

        if not validate_lat(str(latitude.data)):
            raise ValidationError('Please enter a valid latitude (-90 and +90) in degrees decimal.  e.g.-34.407279')

    def validate_longitude(self, longitude):

        if not validate_long(str(longitude.data)):
            raise ValidationError('Please enter a valid longitude (-180 and +180) in degrees decimal   e.g. 150.676888')

    def validate_altitude(self, altitude):

        try:
            float(str(altitude.data))
        except ValueError:
            raise ValidationError('Please enter a valid number to the nearest meter   e.g. 1503')

    def validate_name(self, name):

        if name.data != self.poi_name.data:
            if not validate_poi_name(name.data):
                raise ValidationError('This name is already used by another point of interest')
