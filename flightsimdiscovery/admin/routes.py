from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flightsimdiscovery.models import User, Pois, Ratings, Flagged, Visited, Favorites
from flask_login import current_user, login_required
from flightsimdiscovery.admin.forms import UpdateDatabaseForm, RunScriptForm
from utilities import get_country_list
from flightsimdiscovery.admin.utilities import update_db, backup_db
from flightsimdiscovery import db


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

        if request.method == 'GET':

            return render_template('update_database.html', form=form)

        elif request.method == 'POST':
        
            if form.validate_on_submit():
                # current_user.username = form.username.dat
                backup_db()
                update_db(form.name.data, form.country.data)

                flash('Database has been updated!', 'success')
            
                return redirect(url_for('main.home'))

            else:
                return render_template('update_database.html', form=form)

        else:

            abort(403)

    else:
        abort(403)

@admin.route("/run_script", methods=['GET', 'POST'])
@login_required
def run_script():
    form = RunScriptForm()

    if current_user.is_authenticated and (current_user.username == 'admin'):

        if request.method == 'GET':

            return render_template('run_script.html', form=form)

        elif request.method == 'POST':
        
            if form.validate_on_submit():

                # SCRIPT DETAILS GOES HERE

                all_ratings = Ratings.query.all()

                for rating in all_ratings:

                    poi = Pois.query.get(rating.poi_id)

                    if not poi:
                        print('deleting rating with POI ID = ', rating.poi_id )
                        db.session.delete(rating)
                        
                
                db.session.commit()

                # # check which countries have no pois
                # full_country_list = set(get_country_list())
                # db_country_list = set()
                
                # all_pois = Pois.query.all()

                # for poi in all_pois:
                   
                #     db_country_list.add(poi.country)

                
                # countries_not_in_db = list(full_country_list - db_country_list)
                # for country in countries_not_in_db:
                #     print(country)


                flash('Script has run succesfully!', 'success')
            
                return render_template('run_script.html', form=form)

            else:
                flash('ERROR running the script!', 'danger')
                return render_template('run_script.html', form=form)

        else:

            abort(403)

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

            users_favorited = Favorites.query.filter_by(user_id=user.id).all()
            no_of_user_favorites = 0
            if users_favorited:
                no_of_user_favorites = len(users_favorited)

            users_visited = Visited.query.filter_by(user_id=user.id).all()
            no_of_user_visited = 0
            if users_visited:
                no_of_user_visited = len(users_visited)

            users_rating = Ratings.query.filter_by(user_id=user.id).all()
            no_of_user_ratings = 0
            if users_rating:
                no_of_user_ratings = len(users_rating)

            users_flagged = Flagged.query.filter_by(user_id=user.id).all()
            no_of_user_flagged = 0
            if users_flagged:
                no_of_user_flagged = len(users_flagged)

            user_details['id'] = user.id
            user_details['username'] = user.username
            user_details['number_pois'] = no_of_user_pois
            user_details['number_favorited'] = no_of_user_favorites
            user_details['number_visited'] = no_of_user_visited
            user_details['number_rated'] = no_of_user_ratings
            user_details['number_flagged'] = no_of_user_flagged

            users_data.append(user_details)


        return render_template('user_details.html', users_data=users_data)
    
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

# @admin.route("/build_db")
# @login_required
# def build_db():
#     # open spreadsheet

#     workbook = load_workbook(filename="flightsimdiscovery\\output\\poi_database.xlsx")
#     sheet = workbook.active
#     print("######################")
#     print(sheet.cell(row=10, column=3).value)

#     print('Building dadtabase')

#     if (current_user.username == 'admin') and (False):

#         # Test Create
#         # user_id = 1  # admin will create all these
#         user_id = current_user.id

#         for count, row in enumerate(sheet.rows, start=1):
#             print(count)
#             if count == 1:
#                 continue  # dont include header

#             if row[0].value == "":
#                 break  # no more data in spreadhseet

#             poi = Pois(
#                 user_id=user_id,
#                 name=row[0].value.strip(),
#                  latitude=float(row[2].value),
#                 longitude=float(row[3].value),
#                 region=get_country_region(row[4].value),
#                 country=row[4].value, category=row[1].value,
#                 description=row[6].value
#             )

#             db.session.add(poi)
#             db.session.commit()

#             # Update Rating table
#             # print('Poi ID is: ', poi.id) # This gets the above poi that was just committed.
#             rating = Ratings(user_id=user_id, poi_id=poi.id, rating_score=4)
#             db.session.add(rating)
#             db.session.commit()

#         flash('Database has been built', 'success')
#         return redirect(url_for('main.home'))
#     else:

#         abort(403)

# @admin.route("/create_db")
# def create_db():
#     print("Creating new database")
#     db.create_all()

#     return "success"

