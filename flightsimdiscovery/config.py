import os
import json

# used in production
# with open('/etc/config.json') as config_file:
#     config = json.load(config_file)

# class Config:
#     SECRET_KEY = config.get('FSDISCOVERY_SK')
#     SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
#     MAIL_SERVER = 'smtp.googlemail.com'
#     MAIL_PORT = 587
#     MAIL_USE_TLS = True
#     MAIL_USERNAME = config.get('EMAIL_USER')
#     MAIL_PASSWORD = config.get('EMAIL_PASS')

class Config:
    SECRET_KEY = os.environ.get('FSDISCOVERY_SK')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
