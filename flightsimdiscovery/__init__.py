from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flightsimdiscovery.config import Config

# app = Flask(__name__)
# # PUT THIS IN IN A ENVIRON VARIABLE DONE DIFFERENTLY ON WINDOWS AND LINUX
# app.config['SECRET_KEY'] = os.environ.get('FSDISCOVERY_SK')   # prevents website attacks, cookie manipulation
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)
#
# bcrypt = Bcrypt(app)
#
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'  #function name of our login route
# login_manager.login_message_category = 'info'
#
# #Customize these depending on email account
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
# mail = Mail(app)

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    # app.config.from_object(Config)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flightsimdiscovery.users.routes import users
    from flightsimdiscovery.pois.routes import pois
    from flightsimdiscovery.main.routes import main
    from flightsimdiscovery.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(pois)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app