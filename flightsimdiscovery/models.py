from datetime import datetime
from flightsimdiscovery import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    # pois_visited = db.Column(db.ARRAY, nullable=True)

    # how the object is printed out
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Pois(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    latitude = db.Column(db.FLOAT, unique=False, nullable=False)
    longitude = db.Column(db.FLOAT, unique=False, nullable=False)
    region = db.Column(db.String(20), unique=False, nullable=False)
    country = db.Column(db.String(60), unique=False, nullable=False)
    category = db.Column(db.String(20), unique=False, nullable=False)
    description = db.Column(db.Text, nullable=True)
    nearest_icao_code = db.Column(db.String(4), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Pois('{self.name}', '{self.country}', '{self.category}', '{self.rating}')"

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

# class Visited(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'), nullable=False)

#     def __repr__(self):
#         return f"Visited('{self.user_id}', '{self.poi_id}')"