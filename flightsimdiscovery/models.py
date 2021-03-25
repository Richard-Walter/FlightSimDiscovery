from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flightsimdiscovery import db, login_manager
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.sql import expression


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    volanta_export_path = db.Column(db.String(120), nullable=False, server_default="", default='')
    show_my_flights_check = db.Column(db.Boolean(), nullable=False, server_default=expression.false(), default=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # how the object is printed out
    def __repr__(self):
        return f"User('{self.username}')"


class Pois(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=False)
    latitude = db.Column(db.FLOAT, unique=False, nullable=False)
    longitude = db.Column(db.FLOAT, unique=False, nullable=False)
    region = db.Column(db.String(20), unique=False, nullable=False)
    country = db.Column(db.String(60), unique=False, nullable=False)
    category = db.Column(db.String(20), unique=False, nullable=False)
    description = db.Column(db.Text, nullable=True)
    nearest_icao_code = db.Column(db.String(4), nullable=True)
    # rating = db.Column(db.Integer, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    share = db.Column(db.Boolean(), nullable=False, default=True)
    flag = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f"Pois('{self.name}', '{self.country}', '{self.category}')"


class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'), nullable=False)
    rating_score = db.Column(db.Integer, nullable=True)
    date_rated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Ratings('{self.user_id}', '{self.rating_score}')"


class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'), nullable=False)

    def __repr__(self):
        return f"Favorites('{self.user_id}', '{self.poi_id}')"


class Visited(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'), nullable=False)

    def __repr__(self):
        return f"Visited('{self.user_id}', '{self.poi_id}')"

class Flagged(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f"Flagged('{self.user_id}', '{self.poi_id}', '{self.reason}')"

class Flightplan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    alitude = db.Column(db.Integer, nullable=False, default=5000)
    date_created = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    number_flown = db.Column(db.Integer, nullable=True, default=0)

    def __repr__(self):
        return f"Flight Plan('{self.name}', '{self.alitude}', '{self.user_id}')"       

class Flightplan_Waypoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flightplan_id = db.Column(db.Integer, db.ForeignKey('flightplan.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'), nullable=False)

    def __repr__(self):
        return f"Flight Plan Waypoints('{self.user_id}', '{self.flightplan_id}', '{self.poi_id}')"

class FP_Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flightplan_id = db.Column(db.Integer, db.ForeignKey('flightplan.id'), nullable=False)
    rating_score = db.Column(db.Integer, nullable=True)
    date_rated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"FP_Ratings('{self.fp_id}', '{self.rating_score}')"
