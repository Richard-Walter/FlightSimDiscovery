import os
import json
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))
config_dir = Path(basedir).parents[1]
support_dir = os.path.join(config_dir, 'FSDSupport')
database_URI = 'sqlite:///' + str(support_dir) + '//fsdiscovery.db'
config_file = str(support_dir) + '//CONFIG.json'

mode = ''

try:
    with open(config_file) as config_file:
        config = json.load(config_file)
        mode = config['config']

except FileNotFoundError:
    print('cant find config file - assume production')
    pass

class Config:

    if mode == 'DEVELOPMENT':

        SECRET_KEY = os.environ.get('FSDISCOVERY_SK')
        # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
        SQLALCHEMY_DATABASE_URI = database_URI
        MAIL_SERVER = 'smtp.googlemail.com'
        MAIL_PORT = 587
        MAIL_USE_TLS = True
        MAIL_USERNAME = os.environ.get('EMAIL_USER')
        MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
        GM_KEY = os.environ.get('GM_KEY')

    else: # production

        with open('/etc/config.json') as config_file:
            prod_config = json.load(config_file)

        SECRET_KEY = prod_config.get('FSDISCOVERY_SK')
        # SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
        SQLALCHEMY_DATABASE_URI = database_URI
        MAIL_SERVER = 'smtp.googlemail.com'
        MAIL_PORT = 587
        MAIL_USE_TLS = True
        MAIL_USERNAME = prod_config.get('EMAIL_USER')
        MAIL_PASSWORD = prod_config.get('EMAIL_PASS')
        GM_KEY = prod_config.get('GM_KEY')
    
