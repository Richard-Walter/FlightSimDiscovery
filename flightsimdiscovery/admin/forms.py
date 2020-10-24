from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError

class UpdateDatabaseForm(FlaskForm):

    # name = SelectField('Name', choices=get_xml_db_update_list(), validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_password(self, password):
        if password != 'ginny':

            raise ValidationError('Incorrect password')

    def validate_database_backedup(self, database_backedup):
        if database_backedup != 'Yes':

            raise ValidationError('Please backup database first')


class RunScriptForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Run Script')

    def validate_password(self, password):
        if password != 'ginny':

            raise ValidationError('Incorrect password')

    def validate_database_backedup(self, database_backedup):
        if database_backedup != 'Yes':

            raise ValidationError('Please backup database first')
