import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flightsimdiscovery import app, db, bcrypt
from flightsimdiscovery.forms import RegistrationForm, LoginForm, UpdateAccountForm, PoiForm
from flightsimdiscovery.models import User, Pois
from flask_login import login_user, current_user, logout_user, login_required

# example data that needs to be created from database and then posted to home.html
data = [
  { 'name': 'Home', 'category': 'Bush airport', 'country': 'Australia', 'description': 'Awesome remote bush strip', 'rating': '5','icon': 'http://maps.google.com/mapfiles/ms/micons/pink-pushpin.png', 'lat': -34.44315867450577, 'lng': 150.84022521972656 },
  { 'name': 'Work', 'category': 'Sea base', 'country': 'Vietnam', 'description': 'Great water landing', 'rating': '4', 'icon': 'http://maps.google.com/mapfiles/ms/micons/pink-pushpin.png', 'lat': -35.284, 'lng': 150.833 },
  { 'name': 'Airport', 'category': 'National Park', 'country': 'Congo', 'description': 'Giant trees in mountains areas', 'rating': '3', 'icon': '/static/img/marker/map-mark.png', 'lat': -35.123, 'lng': 150.534 },
]

@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    return render_template("home.html", pois=data)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    # randomize the users profile picture so it doesn't conflict with another user
    random_hex = secrets.token_hex(8)
    # f_name, f_ext = os.path.splitext(form_picture.filename) # This returns file name and file extension.  we just want extension
    _, f_ext = os.path.splitext(form_picture.filename) # This returns file name and file extension.  we just want extension
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/profile_pics', picture_fn)

    # form_picture.save(picture_path)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@login_required
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file  #image file is what we defined in our models.py
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash('Your account has been updated!', 'success')
        # want to redirect instead of render template so a get request is called instead of  post saying form resubmissions
        return redirect(url_for('account')) 
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)




@app.route("/poi/new", methods=['GET', 'POST'])
# @login_required
def new_poi():
    form = PoiForm()
    if form.validate_on_submit():
        poi = Pois(name=form.name.data, latitude=float(form.latitude.data), longitude=float(form.longitude.data),
                 region='Dummy region', country=form.country.data, category=form.category.data, description=form.description.data,
                 nearest_icao_code=form.nearest_airport.data, rating=5)
        db.session.add(poi)
        db.session.commit()
        flash('A new point of interest has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_poi.html', form=form, legend='New Poi')


    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(50), unique=True, nullable=False)
    # latitude = db.Column(db.FLOAT, unique=False, nullable=False)
    # longitude = db.Column(db.FLOAT, unique=False, nullable=False)
    # region = db.Column(db.String(20), unique=False, nullable=False)
    # country = db.Column(db.String(60), unique=False, nullable=False)
    # category = db.Column(db.String(20), unique=False, nullable=False)
    # description = db.Column(db.Text, nullable=True)
    # nearest_icao_code = db.Column(db.String(4), nullable=True)
    # rating = db.Column(db.Integer, nullable=True)
    # date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)



    # name = StringField('Name', validators=[DataRequired()])
    # country = StringField('Country', validators=[DataRequired()])
    # category = StringField('Category', validators=[DataRequired()])
    # description = TextAreaField('Category', validators=[DataRequired()])
    # latitude = StringField('Latitude', validators=[DataRequired(), Length(min=4, max=4)]])
    # longitude = StringField('Longitude', validators=[DataRequired()])
    # nearest_airport = StringField('nearest_airport (ICAO)', validators=[DataRequired(), Length(min=3, max=14)]])

# @app.route("/poi/<int:poi_id>")
# def poi(pooi_id):
#     poi = Poi.query.get_or_404(poi_id)
#     return render_template('poi.html', title=poit.title, poit=poi)


# @app.route("/poi/<int:poi_id>/update", methods=['GET', 'POST'])
# # @login_required
# def update_post(poi_id):
#     poi = Poi.query.get_or_404(poi_id)
#     if post.author != current_user:
#         abort(403)
#     form = PoiForm()
#     if form.validate_on_submit():
#         poi.title = form.title.data
#         poi.content = form.content.data
#         db.session.commit()
#         flash('Your post has been updated!', 'success')
#         return redirect(url_for('poi', post_id=poi.id))
#     elif request.method == 'GET':
#         form.title.data = poi.title
#         form.content.data = poi.content
#     return render_template('create_post.html', title='Update Post',
#                            form=form, legend='Update Post')


# @app.route("/poi/<int:poi_id>/delete", methods=['POST'])
# @login_required
# def delete_post(poi_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author != current_user:
#         abort(403)
#     db.session.delete(post)
#     db.session.commit()
#     flash('Your post has been deleted!', 'success')
#     return redirect(url_for('home'))