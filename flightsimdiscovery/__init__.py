from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '100d56df75a29ea6717b1db3436e06b8'   # prevents website attacks, cookie manipulation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from flightsimdiscovery import routes