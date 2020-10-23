from flask import render_template, url_for, flash, redirect, request, Blueprint
from flightsimdiscovery import db
from flightsimdiscovery.models import User, Pois, Visited, Favorites, Ratings, Flagged
from flask_login import login_user, current_user, logout_user, login_required
from flightsimdiscovery.admin.forms import UpdateDatabaseForm, MigrateDatabaseForm, RunScriptForm

admin = Blueprint('admin', __name__)

@admin.route("/flagged_pois", methods=['GET'])
@login_required
def flagged_pois():

    if current_user.is_authenticated and (current_user.username == 'admin'):

        flagged_pois_data = []
        flagged_pois = Flagged.query.all()
        
        for flagged_poi in flagged_pois:

            poi = Pois.query.filter_by(id=flagged_poi.poi_id).first()
            user = User.query.filter_by(id=flagged_poi.user_id).first()
            data_location = str(poi.latitude) + ', ' + str(poi.longitude)
            date_flagged = flagged_poi.date_posted

            if date_flagged is None:
                date_flagged = ''
            else:
                date_flagged = date_flagged.strftime("%Y-%m-%d %H:%M:%S")

            flagged_poi_data = {'user_id': flagged_poi.user_id, 'username': user.username, 'poi_id': poi.id, 'name': poi.name, 'date_posted': date_flagged,'reason': flagged_poi.reason, 'location': data_location}  
            flagged_pois_data.append(flagged_poi_data) 
        
        return render_template('flagged_pois.html', flagged_pois_data=flagged_pois_data)
    
    else:
        abort(403)
        
@admin.route("/update_database", methods=['GET', 'POST'])
@login_required
def update_database():

    form = UpdateDatabaseForm()

    if current_user.is_authenticated and (current_user.username == 'admin'):

        if form.validate_on_submit():
            # current_user.username = form.username.dat

            flash('Database has been updated!', 'success')
        
            return redirect(url_for('main.home'))

        elif request.method == 'GET':
            # form.username.data = current_user.username

            return render_template('update_database.html', form=form)
    
    else:
        abort(403)

@admin.route("/run_script", methods=['GET', 'POST'])
@login_required
def run_script():
    form = RunScriptForm()

    if current_user.is_authenticated and (current_user.username == 'admin'):

        if form.validate_on_submit():
            # current_user.username = form.username.dat

            flash('Script has been run!', 'success')
            return redirect(url_for('main.home'))

        elif request.method == 'GET':
            # form.username.data = current_user.username


            return render_template('run_script.html', form=form)
    
    else:
        abort(403)

@admin.route("/user_details", methods=['GET', 'POST'])
@login_required
def user_details():
    if current_user.is_authenticated and (current_user.username == 'admin'):

        users_data = []
        users = User.query.all()
        

        for user in users:

            user_details = {}

            users_pois = Pois.query.filter_by(user_id=user.id).all()
            no_of_user_pois = 0
            if users_pois:
                no_of_user_pois = len(users_pois)

            users_rating = Ratings.query.filter_by(user_id=user.id).all()
            no_of_user_ratings = 0
            if users_rating:
                no_of_user_ratings = len(users_pois)

            users_flagged = Flagged.query.filter_by(user_id=user.id).all()
            no_of_user_flagged = 0
            if users_flagged:
                no_of_user_flagged = len(users_pois)

            user_details['id'] = user.id
            user_details['username'] = user.username
            user_details['number_pois'] = no_of_user_pois
            user_details['number_rated'] = no_of_user_ratings
            user_details['number_flagged'] = no_of_user_flagged

            users_data.append(user_details)


        return render_template('user_details.html', users=users_data)
    
    else:
        abort(403)
        

@admin.route("/all_pois")
@login_required
def all_pois():
    all_pois_data = []
    if current_user.is_authenticated and (current_user.username == 'admin'):
        
        all_pois = Pois.query.all()
        flagged_pois = Flagged.query.all()
        flagged_pois_id_list = [flagged_poi.poi_id for flagged_poi in flagged_pois]
        for poi in all_pois:
            # check if poi has been flagged from the Flag table
            poi_flagged = False
            if poi.id in flagged_pois_id_list:
                poi_flagged = True

            user = User.query.filter_by(id=poi.user_id).first()
            data_location = str(poi.latitude) + ', ' + str(poi.longitude)
            poi_data = {'username': user.username, 'id': poi.id, 'location': data_location, 'name': poi.name, 'date_posted': poi.date_posted.strftime("%Y-%m-%d %H:%M:%S"), 'category': poi.category,
                             'country': poi.country, 'region': poi.region,'description': poi.description, 'flag': poi_flagged}   
            all_pois_data.append(poi_data)       

        return render_template('all_pois.html', all_pois=all_pois_data)
    else:
        return render_template('errors/403.html'), 403


