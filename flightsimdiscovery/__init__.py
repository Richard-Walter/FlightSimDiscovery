from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flightsimdiscovery.config import Config
from logging import FileHandler, WARNING
from flightsimdiscovery.config import support_dir

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
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):

    app = Flask(__name__)

    # set up logging
    error_log_file_path  = str(support_dir) + '//error_log.txt'
    file_handler = FileHandler(error_log_file_path)
    file_handler.setLevel(WARNING)
    app.logger.addHandler(file_handler)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flightsimdiscovery.users.routes import users
    from flightsimdiscovery.pois.routes import pois
    from flightsimdiscovery.main.routes import main
    from flightsimdiscovery.admin.commands import scriptsbp
    from flightsimdiscovery.admin.routes import admin
    from flightsimdiscovery.flightplans.routes import flightplans
    from flightsimdiscovery.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(pois)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(scriptsbp)
    app.register_blueprint(flightplans)
    app.register_blueprint(errors)

    return app