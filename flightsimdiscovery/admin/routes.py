from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from sqlalchemy.sql.expression import null
from sqlalchemy import or_
from wikipedia.exceptions import DisambiguationError
from flightsimdiscovery.models import User, Pois, Ratings, Flagged, Visited, Favorites, Flightplan, Flightplan_Waypoints
from flask_login import current_user, login_required
from flightsimdiscovery.admin.forms import UpdateDatabaseForm, RunScriptForm, UpdatePOIDescriptionSelectCriteriaForm
from utilities import get_elevation
from flightsimdiscovery.admin.utilities import update_db, backup_db
from flightsimdiscovery import db
from flightsimdiscovery.main.routes import default_airports
from flightsimdiscovery.flightplans.utils import strip_end
import uuid
import json
from xml.dom import minidom
import xml.etree.ElementTree as ET 
from requests import get
import csv
import os
from tempfile import NamedTemporaryFile
import time
from datetime import datetime, timedelta
import wikipedia


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


# @admin.route("/update_database", methods=['GET', 'POST'])
# @login_required
# def update_database():
#     form = UpdateDatabaseForm()

#     if current_user.is_authenticated and (current_user.username == 'admin'):

#         if request.method == 'GET':

#             return render_template('update_database.html', form=form)

#         elif request.method == 'POST':

#             if form.validate_on_submit():
#                 # current_user.username = form.username.dat
#                 backup_db()
#                 update_db(form.name.data, form.country.data)

#                 flash('Database has been updated!', 'success')

#                 return redirect(url_for('main.home'))

#             else:
#                 return render_template('update_database.html', form=form)

#         else:

#             abort(403)

#     else:
#         abort(403)

# this script determins if a default airport should not be shown, due to a POI for this airport already exist.
# RUn this script LOCALLY after each update
# @admin.route("/update_airports_csv", methods=['GET', 'POST'])
# @login_required
# def update_airports_csv():

#     no_airports_updated = 0

#     form = RunScriptForm()

#     if current_user.is_authenticated and (current_user.username == 'admin'):

#         if request.method == 'GET':

#             return render_template('run_script.html', form=form)

#         elif request.method == 'POST':

#             if form.validate_on_submit():

#                 msfs_airport_list = []
#                 airport_data = {}
#                 airports_updated = []
#                 airports_poi_list = []

                
                    
#                 csv_filepath = os.path.join("flightsimdiscovery/data", "FSD_airports" + "." + "csv")
#                 csv_filepath_temp = os.path.join("flightsimdiscovery/data", "FSD_airports_temp" + "." + "csv")
#                 fields = ['ICAO','Airport_Name','City','Elevation','Longitude','Latitude','tower_frequency','atis_frequency','awos_frequency','asos_frequency','unicom_frequency','Show_on_map']

#                 with open(csv_filepath, encoding="utf-8") as csv_file:

#                     csv_reader = csv.DictReader(csv_file, fieldnames=fields, delimiter=',')
#                     line_count = 0
#                     for row in csv_reader:
#                         if line_count == 0:
                            
#                             line_count += 1
#                         else:
                        
#                             airport_data = {'ICAO': row['ICAO'], 'Airport_Name': row['Airport_Name'], 'City': row['City'], 'Elevation': float(row['Elevation']), 'Longitude': float(row['Longitude']), 'Latitude': float(row['Latitude']), 'tower_frequency': row['tower_frequency'], 'atis_frequency': row['atis_frequency'],'awos_frequency': row['awos_frequency'],'asos_frequency': row['asos_frequency'],'unicom_frequency': row['unicom_frequency'],'Show_on_map': row['Show_on_map']}
#                             line_count += 1
#                             msfs_airport_list.append(airport_data)

#                 exluded_pois = Pois.query.filter(or_(Pois.category == 'Airport (Bush Strip)', Pois.category  == 'Airport (Famous/Interesting)'))

#                 try:

#                     for poi in exluded_pois:
#                         if poi.share == 1:
#                             airports_poi_list.append(poi.name)
#                             # poi_name_first_word = poi.name.split()[0]

#                         # locations are similar.  If so, update csv to not show on map
#                         location_tolerance = 0.03

#                         for airport in msfs_airport_list:

#                             # if (poi.name   == 'Narsarsuaq Airport') and ('Narsarsuaq' in airport['Airport_Name']) :
#                             #     print('stop')
                                
#                             latitude_diff = abs(float(poi.latitude) - airport['Latitude'])
#                             longitude_diff = abs(float(poi.longitude) - airport['Longitude'])

#                             if (latitude_diff < location_tolerance) and (longitude_diff < location_tolerance):
                                
#                                 print("Updating CSV to not show airport " + poi.name)  
#                                 airport['Show_on_map'] = 0
#                                 no_airports_updated +=1
#                                 airports_updated.append(poi.name)
                    
#                     #Update csv
#                     with open(csv_filepath_temp, 'w',encoding="utf-8", newline='') as csv_writer:
#                         writer = csv.DictWriter(csv_writer, fieldnames=fields)
#                         writer.writeheader()
#                         for airport in msfs_airport_list:
#                             writer.writerow(airport)
                                    
#                 except Exception as e:
#                     traceback.print_exc()
#                     flash('ERROR running the script!', 'danger')
#                     return render_template('run_script.html', form=form)
                       
#                 else:
#                     shutil.move(csv_filepath_temp, csv_filepath)
#                     print("Number of airports not showing on map is " + str(no_airports_updated))    
                    
#                     airports_not_updated = (list(set(airports_poi_list) - set(airports_updated)))   
#                     print("\nAirports not updated:  " + str(len(airports_not_updated))) 
#                     print(airports_not_updated)
#                     print('\n')
#                     flash('Script has run succesfully!', 'success')

#                     return render_template('run_script.html', form=form)

#             else:
#                 flash('ERROR running the script!', 'danger')
#                 return render_template('run_script.html', form=form)

#         else:

#             abort(403)

#     else:
#         abort(403)

# This function generates update any pois with missing elevation.  Best torun this script in the morning.
# You may need to run this script multiple times as opem-elevation api times-out regularly.  
# It also generates an xml file in output that is used by MSFS SDK to build a list of POIs to import into the game
# @admin.route("/update_fsd_pois_xml", methods=['GET', 'POST'])
# @login_required
# def update_fsd_pois_xml():
#     form = RunScriptForm()

#     if current_user.is_authenticated and (current_user.username == 'admin'):

#         if request.method == 'GET':

#             return render_template('run_script.html', form=form)

#         elif request.method == 'POST':

#             # generate updates xml file in the output directory if password valid
#             if form.validate_on_submit():

#                 # gm_key = Config.GM_KEY

#                 msfs_pois = ['MSFS Enhanced Airport', 'MSFS Photogrammetry City', 'MSFS Point of Interest']

#                 count_pois_no_elevation_retrieved = 0
                
#                 xml_text = ''
#                 pois = Pois.query.all()
#                 root = ET.Element('FSData', version="9.0") 
#                 tree = ET.ElementTree(root)           

#                 for poi in pois:
                    
#                     share_poi = poi.share
#                     poi_description = poi.description

#                     # dont include private pois
#                     if not share_poi:
#                         continue

#                     # dont incluse any msfs pois
#                     # if any(x in poi_description for x in msfs_pois):
#                     #     continue

#                     unique_id =  str(uuid.uuid4())
#                     poi_lat = str(poi.latitude)
#                     poi_lng = str(poi.longitude)
#                     poi_alt = poi.altitude

#                     # only get elevation if it doesnt alreay exist in the database
#                     if poi_alt is null:
#                         try:
#                             print("TRYING TO GET POI ELEVATION: " + str(poi.id) + "   " + poi.name + " " + poi_lat + "  " + poi_lng)
#                             poi_alt = get_elevation(poi_lat, poi_lng)
#                         except Exception as e:  
#                             print(e)
#                             continue

#                         if poi_alt is not None:

#                             # update database poi with new elevation
#                             poi_to_update = Pois.query.get_or_404(poi.id)
#                             poi_to_update.altitude = poi_alt
#                             db.session.commit()
#                             print("ADDED POI ELEVATION: " + str(poi.id) + "   " + poi.name + "   " + str(poi_alt))
#                         else:
#                             count_pois_no_elevation_retrieved += 1
                            
#                             print(count_pois_no_elevation_retrieved)
                    
#                     landmark_location = ET.SubElement(root, 'LandmarkLocation', instanceId = unique_id, type="POI", name=poi.name, lat=poi_lat, lon=poi_lng, alt=str(poi_alt), offset='0.000000')
                
                
#                 xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
#                 with open('flightsimdiscovery/output/fsd_pois.xml', 'wb') as f:
#                     f.write(xmlstr.encode('utf-8'))

#                 flash('POIS XML has run succesfully!  Please check the output folder and copy over to the MSFS SDK FSD POIS directory', 'success')

#                 return render_template('run_script.html', form=form)

#             else:
#                 flash('ERROR running the script!', 'danger')
#                 return render_template('run_script.html', form=form)

#         else:

#             abort(403)

#     else:
#         abort(403)

# must have a pois.json file in the input directory.  THis can be generated from DB Browser export table as JSON
# It will read alititudes for each poi in the JSON file an update the correspoing POI in the production database
@admin.route("/update_proudction_pois_elevation", methods=['GET', 'POST'])
@login_required
def update_proudction_pois_elevation():
    form = RunScriptForm()

    if current_user.is_authenticated and (current_user.username == 'admin'):

        if request.method == 'GET':

            return render_template('run_script.html', form=form)

        elif request.method == 'POST':

            # generate updates xml file in the output directory if password valid
            if form.validate_on_submit():

                pois_updated = 0
                
                # Opening JSON file
                with open('flightsimdiscovery/input/pois.json', encoding="utf8") as json_file:
                    json_pois_list = json.load(json_file)

                    for json_poi in json_pois_list:
                        json_poi_id = json_poi['id']
                        json_poi_alt = json_poi['altitude']
                        
                        # update database with altitude
                        if json_poi_alt is not null:
                            # update database poi with new elevation
                            print(json_poi_id)
                            poi_to_update = Pois.query.get(json_poi_id)

                            # for some reason export json file includes previous deleted pois
                            if poi_to_update:

                                # only update elevations if they are null or 0
                                if not poi_to_update.altitude:
                                    poi_to_update.altitude = json_poi_alt
                                    db.session.commit()
                                    print("UPDATED POI WITH NEW ELEVATION: " + str(json_poi_id) + "   " + str(json_poi_alt))
                                    pois_updated += 1

 

                flash('POIS elevation updated has run succesfully!  Number of pois updated with elevation is ' + str(pois_updated), 'success')

                return render_template('run_script.html', form=form)

            else:
                flash('ERROR running the script!', 'danger')
                return render_template('run_script.html', form=form)

        else:

            abort(403)

    else:
        abort(403)


#  this method filters pois that may need there descriptions updated based on certain criteria that can be specified in a form
@admin.route("/update_poi_description", methods=['GET', 'POST'])
@login_required
def update_poi_description():

    form = UpdatePOIDescriptionSelectCriteriaForm()

    if current_user.is_authenticated and (current_user.username == 'admin'):

        if request.method == 'GET':

            return render_template('update_poi_description_criteria.html', form=form)

        elif request.method == 'POST':

            # generate updates xml file in the output directory if password valid
            if form.validate_on_submit():
                
                filtered_pois = []
                

                category = form.category.data
                word_limit = form.word_limit.data

                time_exclusion = int(form.time_exclusion.data)
                current_time_utc = datetime.utcnow

                pois = Pois.query.all()      

                for poi in pois:

                    poi_description = poi.description
                    poi_description_word_count = len(poi_description.split())

                    # exclude private pois
                    # if (not poi.share) or (poi.category != category) or (poi_description_word_count > word_limit):
                    if (not poi.share):
                        continue
                    
                    if form.category.data != 'All':
                        if poi.category != category:
                            if (category == 'MSFS Point of Interest') or (category == 'MSFS Photogrammetry City') :
                                if (category not in poi_description):
                                    if ('MSFS Photogrammery City' not in poi_description):
                                        continue
                            else:
                                continue

                    if poi_description_word_count > word_limit:
                        continue
                        
                    poi_data = {'id': poi.id,'name': poi.name,'category': poi.category,'description': poi.description}
                    filtered_pois.append(poi_data)

                return render_template('filtered_pois.html', filtered_pois=filtered_pois, count = len(filtered_pois))

            else:
                flash('ERROR running the script!', 'danger')
                return render_template('run_script.html', form=form)

        else:

            abort(403)

    else:
        abort(403)

# #  update new enhanced airports/airport POIS with ICAO which is used as a lookup to add coms to the infowindow
# @admin.route("/update_icao", methods=['GET', 'POST'])
# @login_required
# def update_icao():
#     form = RunScriptForm()

#     if current_user.is_authenticated and (current_user.username == 'admin'):

#         if request.method == 'GET':

#             return render_template('run_script.html', form=form)

#         elif request.method == 'POST':

#             # generate updates xml file in the output directory if password valid
#             if form.validate_on_submit():
                
#                 location_tolerance = 0.03
#                 no_airports_updated = 0
#                 airports_updated = []
                
#                 pois = Pois.query.all()      

#                 for poi in pois:
#                     if ('Airport' in poi.category) and (not poi.nearest_icao_code):
                        
#                         # look up ICAO from MSFS default airports and update
#                         for airport in default_airports:

#                             latitude_diff = abs(float(poi.latitude) - airport['lat'])
#                             longitude_diff = abs(float(poi.longitude) - airport['lon'])

#                             if (latitude_diff < location_tolerance) and (longitude_diff < location_tolerance):
                                
#                                 poi_to_update = Pois.query.get(poi.id)
#                                 poi_to_update.nearest_icao_code = airport['ICAO']
#                                 db.session.commit()
#                                 print("Updating ICAO of airport " + poi.name + "  " + airport['ICAO'])  
#                                 no_airports_updated +=1
#                                 airports_updated.append(poi.name)

 

#                 flash('POIS elevation updated has run succesfully!  Number of pois updated with elevation is ' + str(no_airports_updated), 'success')

#                 return render_template('run_script.html', form=form)

#             else:
#                 flash('ERROR running the script!', 'danger')
#                 return render_template('run_script.html', form=form)

#         else:

#             abort(403)

#     else:
#         abort(403)


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

@admin.route("/update_msfs_poi_descriptions")
@login_required
def update_msfs_poi_descriptions():

    no_pois_updated = 0
    no_pois_not_updated = 0
    updated_pois = []


    pois = Pois.query.all()      

    for poi in pois:

        poi_name = ''
        
        # only update poi descriptif it is a new MSFS Point of INterst and hasn't been updated before
        if (poi.description  not in ['MSFS Photogrammery City', 'MSFS Photogrammery City', 'MSFS Point of Interest']):
            continue

        if (poi.description == 'MSFS Photogrammery City'):
            poi.description = 'MSFS Photogrammery City'
            poi_name_list = poi.name.split(',')
            # exlcude county from name as wiki returns county detail rather that the city
            for part_name in poi_name_list:
                if 'County' in part_name:
                    continue
                
                poi_name = poi_name + part_name + ' '

        poi_name = poi_name + ', ' + poi.country
        poi_category = poi.category
        search_name = poi_name + ' ' + poi_category

        try:
            wiki_summary = wikipedia.summary(search_name, sentences=4)

            # wiki search sometimes returns this string for city/town descriptions
            if ('The following is a list of the most populous incorporated places' in wiki_summary):
                continue
            # print(wikipedia.summary(poi_name, sentences=4))
        except wikipedia.exceptions.DisambiguationError:
            print("disamiguation error for poi no. " + str(poi.id))
        except wikipedia.exceptions.PageError:
            print("Page error for poi no. " + str(poi.id) + '  Search was ' + poi_name)
            no_pois_not_updated += 1
        else:

            poi_to_update = Pois.query.get(poi.id)
            poi_to_update.description = 'This is a microsoft flight simulator enhanced ' + poi.description +  '. ' + wiki_summary
            print('UPdating Poi ' + str(poi.id))
            no_pois_updated += 1
            db.session.commit()
            updated_pois.append(poi_to_update)

    return render_template('filtered_pois.html', filtered_pois=updated_pois, count = len(updated_pois))