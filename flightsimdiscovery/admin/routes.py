from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
# from sqlalchemy.sql.expression import null
from flightsimdiscovery.models import User, Pois, Ratings, Flagged, Visited, Favorites, Flightplan, Flightplan_Waypoints
from flask_login import current_user, login_required
from flightsimdiscovery.admin.forms import UpdateDatabaseForm, RunScriptForm
from utilities import get_elevation
from flightsimdiscovery.admin.utilities import update_db, backup_db
from flightsimdiscovery import db
from flightsimdiscovery.flightplans.utils import checkUserFlightPlanWaypointsUnique, get_user_flightplans, updateFlightPlanNumberFlown, strip_end
import uuid
from xml.dom import minidom
import xml.etree.ElementTree as ET 
from requests import get

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

            flagged_poi_data = {'user_id': flagged_poi.user_id, 'username': user.username, 'poi_id': poi.id, 'name': poi.name,
                                'date_posted': date_flagged, 'reason': flagged_poi.reason, 'location': data_location}
            flagged_pois_data.append(flagged_poi_data)

        return render_template('flagged_pois.html', flagged_pois_data=flagged_pois_data)

    else:
        abort(403)

@admin.route("/shared_flightplans", methods=['GET'])
@login_required
def shared_flightplans():
    if current_user.is_authenticated and (current_user.username == 'admin'):

        shared_flightplan_data = []
        flightplans = Flightplan.query.filter_by()

        for flightplan in flightplans:
            user = User.query.filter_by(id=flightplan.user_id).first()

            fp_waypoint_list = ""
            fp_waypoint_query = Flightplan_Waypoints.query.filter_by(flightplan_id=flightplan.id).all()

            for fp_waypoint in fp_waypoint_query:

                # determine the name of the poi
                poi_name = Pois.query.filter_by(id=fp_waypoint.poi_id).first().name
                fp_waypoint_list += poi_name + " -> "
                fp_waypoint_list = strip_end(fp_waypoint_list, " -> ")

            flightplan_data = {'id': flightplan.id, 'user_id': flightplan.user_id, 'user_name': user.username, 'name': flightplan.name,
                                'waypoints': fp_waypoint_list}
            shared_flightplan_data.append(flightplan_data)

        return render_template('shared_flightplans.html', shared_flightplan_data=shared_flightplan_data)

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

                # update flightplan table so number_flown is not null

                # flightplans = Flightplan.query.all()

                # for flightplan in flightplans:
                #     if flightplan.number_flown is None:
                #         flightplan.number_flown = 1
                #         db.session.add(flightplan)
                
                # db.session.commit()

                flash('Script has run succesfully!', 'success')

                return render_template('run_script.html', form=form)

            else:
                flash('ERROR running the script!', 'danger')
                return render_template('run_script.html', form=form)

        else:

            abort(403)

    else:
        abort(403)

# This function generates an xml file in output that is used by MSFS SDK to build a list of POIs to import into the game
@admin.route("/update_fsd_pois_xml", methods=['GET', 'POST'])
@login_required
def update_fsd_pois_xml():
    form = RunScriptForm()

    if current_user.is_authenticated and (current_user.username == 'admin'):

        if request.method == 'GET':

            return render_template('run_script.html', form=form)

        elif request.method == 'POST':

            # generate updates xml file in the output directory if password valid
            if form.validate_on_submit():

                # gm_key = Config.GM_KEY

                msfs_pois = ['MSFS Enhanced Airport', 'MSFS Photogrammery City', 'MSFS Point of Interest']

                count_pois_no_elevation_retrieved = 0
                
                xml_text = ''
                pois = Pois.query.all()
                root = ET.Element('FSData', version="9.0") 
                tree = ET.ElementTree(root)           

                for poi in pois:
                    
                    share_poi = poi.share
                    poi_description = poi.description

                    # dont include private pois
                    if not share_poi:
                        continue

                    # dont incluse any msfs pois
                    if any(x in poi_description for x in msfs_pois):
                        continue

                    unique_id =  str(uuid.uuid4())
                    poi_lat = str(poi.latitude)
                    poi_lng = str(poi.longitude)
                    poi_alt = poi.altitude

                    # only get elevation if it doesnt alreay exist in the database
                    if poi_alt is not None:
                        try:
                            print("TRYING TO GET POI ELEVATION: " + str(poi.id) + "   " + poi.name + " " + poi_lat + "  " + poi_lng)
                            poi_alt = get_elevation(poi_lat, poi_lng)
                        except Exception:  
                            continue

                        if poi_alt:

                            # update database poi with new elevation
                            poi_to_update = Pois.query.get_or_404(poi.id)
                            poi_to_update.altitude = poi_alt
                            db.session.commit()
                            print("ADDED POI ELEVATION: " + str(poi.id) + "   " + poi.name)
                        else:
                            count_pois_no_elevation_retrieved += 1
                            
                            print(count_pois_no_elevation_retrieved)
                    
                    landmark_location = ET.SubElement(root, 'LandmarkLocation', instanceId = unique_id, type="POI", name=poi.name, lat=poi_lat, lon=poi_lng, alt=str(poi_alt), offset='0.000000')
                
                
                xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
                with open('flightsimdiscovery/output/fsd_pois.xml', 'wb') as f:
                    f.write(xmlstr.encode('utf-8'))

                flash('POIS XML has run succesfully!  Please check the output folder and copy over to the MSFS SDK FSD POIS directory', 'success')

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

            users_shared_fp = Flightplan.query.filter_by(user_id=user.id).all()
            no_of_user_fp_shared = 0
            if users_shared_fp:
                no_of_user_fp_shared = len(users_shared_fp)

            user_details['id'] = user.id
            user_details['username'] = user.username
            user_details['number_pois'] = no_of_user_pois
            user_details['number_favorited'] = no_of_user_favorites
            user_details['number_visited'] = no_of_user_visited
            user_details['number_rated'] = no_of_user_ratings
            user_details['number_flagged'] = no_of_user_flagged
            user_details['number_fp_shared'] = no_of_user_fp_shared

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
            poi_data = {'username': user.username, 'id': poi.id, 'location': data_location, 'name': poi.name,
                        'date_posted': poi.date_posted.strftime("%Y-%m-%d %H:%M:%S"), 'category': poi.category,
                        'country': poi.country, 'region': poi.region, 'description': poi.description, 'flag': poi_flagged}
            all_pois_data.append(poi_data)

        return render_template('all_pois.html', all_pois=all_pois_data)
    else:
        return render_template('errors/403.html'), 403

@admin.route("/stats")
def stats():

    # USER STATS
    user_data = []
    users = User.query.all()

    for user in users:

        no_poi_visited = 0
        no_poi_created = 0
        no_flights_shared = 0

        #exclude admin and anonymous users
        if (user.id == 1) or (user.id==2):
            continue

        #pois visited by user
        poi_visited = Visited.query.filter_by(user_id=user.id).all()
        if poi_visited:
            no_poi_visited = len(poi_visited)

        #pois created by user
        pois_created = Pois.query.filter_by(user_id=user.id).all()
        if pois_created:
            no_poi_created = len(pois_created)

        #flights shared by user
        flights_shared = Flightplan.query.filter_by(user_id=user.id).all()
        if flights_shared:
            no_flights_shared = len(flights_shared)

        user_info = {'name': user.username, 'pois_visited': no_poi_visited, 'pois_created': no_poi_created, 'flights_shared': no_flights_shared}
        user_data.append(user_info)
    

    # FLIGHT STATS
    popular_flight_data = []

    flightplans = Flightplan.query.all()

    for flightplan in flightplans:

        fp_waypoint_list = ""
        fp_waypoint_query = Flightplan_Waypoints.query.filter_by(flightplan_id=flightplan.id).all()

        for fp_waypoint in fp_waypoint_query:

            # determine the name of the poi
            poi_name = Pois.query.filter_by(id=fp_waypoint.poi_id).first().name
            fp_waypoint_list += poi_name + " -> "
        
        fp_waypoint_list = strip_end(fp_waypoint_list, " -> ")

        flight_data = {'id': flightplan.id, 'popularity': flightplan.number_flown, 'name': flightplan.name,
                            'waypoints': fp_waypoint_list}
        popular_flight_data.append(flight_data)

    # POI STATS
    popular_pois_data = []
    no_poi_visited = 0
    all_pois = Pois.query.all()

    for poi in all_pois:
        poi_visited = Visited.query.filter_by(poi_id=poi.id).all()
        if poi_visited:
            no_poi_visited = len(poi_visited)
        data_location = str(poi.latitude) + ', ' + str(poi.longitude)
        popular_pois = {'popularity': no_poi_visited, 'name': poi.name,'category': poi.category,'country': poi.country, 'region': poi.region, 'description': poi.description, 'location': data_location}
        popular_pois_data.append(popular_pois)

    return render_template('stats.html', popular_pois=popular_pois_data, popular_flight_data=popular_flight_data, user_data=user_data)

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
