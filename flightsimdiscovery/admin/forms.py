from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from flightsimdiscovery.admin.utilities import get_xml_db_update_list
from utilities import get_country_list

class UpdateDatabaseForm(FlaskForm):

    name = SelectField('Name', choices=get_xml_db_update_list())
    country = SelectField('Country', choices=get_country_list(), validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_password(self, password):
        if password.data != 'ginny':

            raise ValidationError('Incorrect password')

    def validate_country(self, country):
        if country.data not in self.name.data:

            raise ValidationError('Selected country name not found in xml file name')


class RunScriptForm(FlaskForm):

    name = SelectField('Name', choices=get_xml_db_update_list())
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Run Script')

    def validate_password(self, password):
        if password != 'ginny':

            raise ValidationError('Incorrect password')

