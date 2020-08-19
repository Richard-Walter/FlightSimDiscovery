from flask import Flask
from flask import render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask import flash
import pygeoj
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = '100d56df75a29ea6717b1db3436e06b8'   # prevents website attacks, cookie manipulation

posts = [
    {
        "author": "Corey Schafer",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2018",
    },
    {
        "author": "Jane Doe",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2018",
    },
]

data = [
  { 'Name': 'Location A', 'category': 'Store', 'street': 'Market', 'lat': -35.984, 'lng': 154.343 },
  { 'Name': 'Location B', 'category': 'House', 'street': 'Broad', 'lat': -35.284, 'lng': 154.833 },
  { 'Name': 'Location C', 'category': 'Office', 'street': 'South', 'lat': -35.123, 'lng': 154.534 },
]

geojson_sample = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "icon": "http://maps.google.com/mapfiles/ms/micons/pink-pushpin.png",
        "marker-color": "#7e7e7e",
        "marker-size": "medium",
        "marker-symbol": "",
        "Name": "Home"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [
          150.84022521972656,
          -34.44315867450577
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "icon": "http://maps.google.com/mapfiles/ms/micons/pink-pushpin.png",
        "marker-color": "#7e7e7e",
        "marker-size": "medium",
        "marker-symbol": "",
        "Name": "Airport"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [
          150.79010009765625,
          -34.55888020163025
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "icon": "/static/img/marker/map-mark.png",
        "marker-color": "#7e7e7e",
        "marker-size": "medium",
        "marker-symbol": "",
        "Name": "Work"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [
          150.78632354736328,
          -34.33606548328852
        ]
      }
    }
  ]
}

# # Create the GEoJSon file to post
# newfile = pygeoj.new()
# newfile.add_feature(properties={"country":"Norway"},
#                     geometry={"type":"Polygon", "coordinates":[[(21,3),(33,11),(44,22)]]} )
# newfile.add_feature(properties={"country":"USA"},
#                     geometry={"type":"Polygon", "coordinates":[[(11,23),(14,5),(66,31)]]} )

@app.route("/")
@app.route("/home")
def home():
    # return '<h1>Home Page<h1>'  # easier to use a template
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))

    return render_template("register.html", title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':

            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful!', 'danger')
    return render_template("login.html", title='Login', form=form) 
        
@app.route("/test")
def test():
    return render_template("test.html", posts=data)
    # return render_template("test.html", posts=newfile)

if __name__ == "__main__":

    app.run(
        debug=True
    )  # this means you dont have to restart the server after each change

