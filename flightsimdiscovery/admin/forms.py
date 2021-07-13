from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from flightsimdiscovery.admin.utilities import get_xml_db_update_list
from utilities import get_country_list, get_category_list

class UpdateDatabaseForm(FlaskForm):

    country_list=get_country_list()
    country_list.insert(0,'Region')

    name = SelectField('Name', choices=get_xml_db_update_list())
    country = SelectField('Country', choices=country_list, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_password(self, password):
        if password.data != 'ginny':

            raise ValidationError('Incorrect password')

    # def validate_country(self, country):
    #     if country.data not in self.name.data:

    #         raise ValidationError('Selected country name not found in xml file name')


class RunScriptForm(FlaskForm):

    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Run Script')

    def validate_password(self, password):
        if password.data != 'ginny':

            raise ValidationError('Incorrect password')

class UpdatePOIDescriptionSelectCriteriaForm(FlaskForm):

    exclude_time_period_hrs = [0, 1,2,3,8,24]

    category = SelectField('Category', choices=get_category_list())
    time_exclusion = SelectField('Exclude recent updates (hrs)', choices=exclude_time_period_hrs, default=0,)
    word_limit = IntegerField('Set Word Limit (integer)', default=20)

    submit = SubmitField('Generate POIs')

    # def validate_country(self, country):
    #     if country.data not in self.name.data:

    #         raise ValidationError('Selected country name not found in xml file name')