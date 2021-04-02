from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, current_app
from flightsimdiscovery import db, bcrypt
from flightsimdiscovery.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flightsimdiscovery.models import User, Pois
from flask_login import login_user, current_user, logout_user, login_required
from flightsimdiscovery.users.utitls import save_picture, send_reset_email, get_user_pois_dict_inc_favorites_visited, get_user_favorited_pois, get_user_visited_pois, get_user_flagged_pois, save_flight_data_to_db
import json, os
from json.decoder import JSONDecodeError

users = Blueprint('users', __name__)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))

    return render_template("register.html", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    user_pois = None
    print(current_user.id)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file  # image file is what we defined in our models.py
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash('Your account has been updated!', 'success')
        # want to redirect instead of render template so a get request is called instead of  post saying form resubmissions
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        # user_pois_with_additional_data = get_user_pois_dict_inc_favorites_visited(current_user.id)
        # print('###### USER POIS ###### ', user_pois_with_additional_data )

    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)

@users.route("/my_flights", methods=['GET', 'POST'])
@login_required
def my_flights():

    json_flight_data_list = []

    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No files found, try again.')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        
        try:
            for file in files:
                flight_text = file.read().decode('utf-8-sig')
                json_flight_data = json.loads(flight_text)
                json_flight_data_list.append(json_flight_data)
            
            #parse volanta json flight data and store in database
            save_flight_data_to_db(json_flight_data_list, 'Volanta')
                
        except  JSONDecodeError:
            print("cannont decode the json file")
            flash("One of the files you have selected does not appear to be a valid volanta JSON file", 'warning')
            return redirect(request.url)

        else:
            return redirect(url_for('main.home', _anchor='google_map'))      

    elif request.method == 'GET':

        return render_template('my_flights.html')

@users.route("/my_flights/delete/<id>",methods=['POST'])
@login_required
def delete_flight(id):
    
    # *** WHEN WE DELETE A FLIGHT, WE HAVE DELETE THE CORRESPONDING FLIGHT WAYPOINTS OUT OF THE OTHER TABLE  ****

    # category = request.args.get('page')
    # poi = Pois.query.get_or_404(poi_id)
    # flagged_poi = Flagged.query.filter_by(poi_id=poi_id).first()

    # # visited and favorite can contain multuple records for the one poi_id
    # visited_poi_list = Visited.query.filter_by(poi_id=poi_id).all()
    # favorited_pois_list = Favorites.query.filter_by(poi_id=poi_id).all()
    # ratings_poi_list = Ratings.query.filter_by(poi_id=poi_id).all()

    # if (current_user.username != 'admin'):
    #     if (poi.user_id != current_user.id):
    #         abort(403)
    # db.session.delete(poi)
    # if flagged_poi:
    #     db.session.delete(flagged_poi)

    # for visited_poi in visited_poi_list:
    #     db.session.delete(visited_poi)
    # for favorited_pois in favorited_pois_list:
    #     db.session.delete(favorited_pois)
    # for ratings_poi in ratings_poi_list:
    #     db.session.delete(ratings_poi)

    # # delete record from flight plan tables that contain poi
    # fp_id_set = set()
    # fp_waypoints_poi_list = Flightplan_Waypoints.query.filter_by(poi_id=poi_id).all()

    # for fp_waypoints_poi in fp_waypoints_poi_list:
    #     fp_id_set.add(fp_waypoints_poi.flightplan_id)

    # for fp_id in fp_id_set:
    #     fp = Flightplan.query.filter_by(id=fp_id).first()
    #     db.session.delete(fp)

    #     fp_rating = FP_Ratings.query.filter_by(flightplan_id=fp_id).first()
    #     db.session.delete(fp_rating)

    #     fp_waypoints = Flightplan_Waypoints.query.filter_by(flightplan_id=fp_id).all()

    #     # delete all waypoints associated with the flight plan as the flight plan is no longer valid
    #     for fp_waypoint in fp_waypoints:
    #         db.session.delete(fp_waypoint)

    # db.session.commit()
    print(id)
    flash('Your flight has been deleted!', 'success')
    print('Your flight has been deleted!')

    return redirect(url_for('main.home'))


@users.route("/user_pois", defaults={'user_id': None})
@users.route("/user_pois/<user_id>")
@login_required
def user_pois(user_id):

    if user_id:
        if (current_user.username != 'admin'):
            if (user_id != str(current_user.id)):
                abort(403)
    else:
        user_id = current_user.id
        
    user_pois_with_additional_data = get_user_pois_dict_inc_favorites_visited(user_id, True)
    favorite_pois = get_user_favorited_pois(user_id)
    visited_pois = get_user_visited_pois(user_id)
    flagged_pois = get_user_flagged_pois(user_id)

    return render_template('user_pois.html', user_pois=user_pois_with_additional_data, favorite_pois=favorite_pois, visited_pois=visited_pois, flagged_pois=flagged_pois)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)
