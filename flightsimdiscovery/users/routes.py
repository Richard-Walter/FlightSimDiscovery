from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, current_app, session, jsonify
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.functions import user
from flightsimdiscovery import db, bcrypt
from flightsimdiscovery.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flightsimdiscovery.models import User, Pois, UserFlights, User_flight_positions, ActiveFlights
from flask_login import login_user, current_user, logout_user, login_required
from flightsimdiscovery.users.utitls import save_picture, send_reset_email, get_user_pois_dict_inc_favorites_visited, get_user_favorited_pois, get_user_visited_pois, get_user_flagged_pois, save_flight_data_to_db, get_user_flights, msfs_encrypt, msfs_decrypt
import json, os
from json.decoder import JSONDecodeError
from datetime import datetime
from flask_cors import cross_origin

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
        current_user.goto_map_home_page = form.goto_map_home_page.data
        db.session.commit()

        flash('Your account has been updated!', 'success')
        # want to redirect instead of render template so a get request is called instead of  post saying form resubmissions
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.goto_map_home_page.data = current_user.goto_map_home_page
        # form.goto_map_home_page.data = current_user.email

    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)

@users.route("/my_flights", methods=['GET', 'POST'])
@login_required
def my_flights():

    user_flights = get_user_flights()

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
                
        except  (JSONDecodeError, TypeError, KeyError):
            print("cannont decode the json file")
            flash("One of the files you have selected does not appear to be a valid volanta JSON file", 'warning')
            return redirect(request.url)

        else:
            flash("Volanta flights successfully uploaded", 'success')
            return redirect(request.url)
            # return redirect(url_for('main.home', _anchor='google_map'))      

    elif request.method == 'GET':

        return render_template('my_flights.html', user_flights=user_flights)

@users.route("/my_flights/delete/<flight_id>",methods=['POST'])
@login_required
def delete_flight(flight_id):
    
    # WHEN WE DELETE A FLIGHT, WE HAVE DELETE THE CORRESPONDING FLIGHT WAYPOINTS OUT OF THE OTHER TABLE

    category = request.args.get('page')
    flight = UserFlights.query.get_or_404(flight_id)

    # each flight can contain multiple waypoints that need to be deleted as well
    flight_waypoint_list = User_flight_positions.query.filter_by(flight_id=flight_id).all()

    # only the user who owns the flight can delete it.
    if (current_user.username != 'admin'):
        if (flight.user_id != current_user.id):
            abort(403)
    db.session.delete(flight)

    for waypoint_poi in flight_waypoint_list:
        db.session.delete(waypoint_poi)

    db.session.commit()
    
    flash('Your flight has been deleted!', 'success')

    if category == 'my_flights':
        return redirect(url_for('users.my_flights'))
    else:
        return redirect(url_for('main.home', _anchor='google_map')) 


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


@users.route('/users/get_user_location',  methods=['GET', 'POST'])
def get_user_location():

    active_flight_info = {}
    user_id = request.form.get("user_id")
    
    if current_user.is_authenticated:
        if current_user.id == int(user_id):
            
            user_active_flight = ActiveFlights.query.filter_by(user_id=user_id).first()

            if user_active_flight:

                active_flight_info['last_update'] = user_active_flight.last_update
                active_flight_info['lat'] = user_active_flight.latitude
                active_flight_info['lng'] = user_active_flight.longitude
                active_flight_info['alt'] = user_active_flight.altitude
                active_flight_info['ias'] = user_active_flight.ias
                active_flight_info['ground_speed'] = user_active_flight.ground_speed
                active_flight_info['heading_true'] = user_active_flight.heading_true

            else:
                print("no active flight in database for this user: " + user_id)
                

        else:
             # current user and msfs user id dont match.
            abort(403) 
 

    return jsonify(active_flight_info)

@users.route('/users/show_active_flight_checkbox',  methods=['GET', 'POST'])
def show_active_flight_checkbox():

    # show_active_flight = request.get_json()
    show_active_flight = request.form.get("showChecked")

    if show_active_flight == 'true':
        show_active_flight = True
    else:
        show_active_flight = False
    
    if current_user.is_authenticated:
            
            user_active_flight = ActiveFlights.query.filter_by(user_id=current_user.id).first()

            if user_active_flight:

                user_active_flight.show_checked = show_active_flight
                db.session.commit()
                return ('Success', 200)
    else:
        return ('User not logged into FSD browser - can not update database', 401)
 


####################################################################
###########   THESE ROUTES COME FROM WITH IN MSFS!   ###############
####################################################################

@users.route('/users/update_active_flight',  methods=['GET', 'POST'])
@cross_origin()  # this decorator is requeired to accepted posts from external clients such as MSFS
def update_active_flight():
       
    sim_connect_data = request.get_json()

    if not sim_connect_data:
        print('Failed-No User ID')
        return ('Failed-No User ID', 401)

    # Check to see if we have any simConnect data, given we have a user_id
    if len(sim_connect_data) >1:


        encrpted_user_id = sim_connect_data['user_id']
        user_id = msfs_decrypt(encrpted_user_id)
        
        lat = sim_connect_data['lat']
        lng = sim_connect_data['lng']
        alt = sim_connect_data['alt']
        ias = sim_connect_data['ias']
        ground_speed = sim_connect_data['ground_speed']
        heading_true = sim_connect_data['heading_true'] 
        
        user_active_flight = ActiveFlights.query.filter_by(user_id=user_id).first()

        if user_active_flight:
            if user_active_flight.show_checked:
                user_active_flight.last_update = datetime.utcnow()
                user_active_flight.latitude = lat
                user_active_flight.longitude = lng
                user_active_flight.altitude = alt
                user_active_flight.ias = ias
                user_active_flight.ground_speed = ground_speed
                user_active_flight.heading_true = heading_true
            else:
                #user has not check show active flight on browser
                print('user has not check show active flight on browser')
                return ('Fail', 204)
        else:

            #  create new user active flight
            active_flight = ActiveFlights(user_id=user_id, latitude=lat, longitude=lng, altitude=alt, ias=ias,ground_speed=ground_speed, heading_true=heading_true)
            db.session.add(active_flight)

        db.session.commit()

        print("SAVING ACTIVE FLIGHT FROM MSFS!!!!!")
        return ('Success', 200)
    
    else:
        print("NO SIMCONNECT DATA")
        return('NO SIMCONNECT DATA', 401)


# validates a MSFS loggin and returns a encrpyted user_id
@users.route('/users/msfs_login',  methods=['GET', 'POST'])
@cross_origin()  # this decorator is requeired to accepted posts from external clients such as MSFS
def msfs_login():

    user_credentials = request.get_json()
    msfs_username = user_credentials['username']
    msfs_password = user_credentials['password']
    user = User.query.filter_by(email=msfs_username).first()

    if user and bcrypt.check_password_hash(user.password, msfs_password):

        #flask automatically converts user_id to json and adds 200 respone code
        encrypted_user_id = msfs_encrypt(user.id)
        return (encrypted_user_id, 200)

    else:
        print("usename and password dont authenticate")
        return ('Failed', 401)

