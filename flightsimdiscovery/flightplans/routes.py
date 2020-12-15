import csv, os, json
import xml.etree.ElementTree as ET
from copy import deepcopy
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, jsonify, after_this_request, make_response
from openpyxl import load_workbook
from flightsimdiscovery import db
from flightsimdiscovery.models import Favorites, Visited, User, Flagged, Flightplan, Flightplan_Waypoints, FP_Ratings
from flask_login import current_user, login_required
from utilities import get_country_region, get_country_list, get_region_list, get_category_list, region_details, countries_details, get_nearest_airport
from flightsimdiscovery.pois.utils import *
from flightsimdiscovery.config import Config
from utilities import get_location_details
from flightsimdiscovery.flightplans.utils import checkUserFlightPlanWaypointsUnique, get_user_flightplans, updateFlightPlanNumberFlown, strip_end

flightplans = Blueprint('flightplans', __name__)

@flightplans.route('/flightplans/build_flightplan', methods=['GET', 'POST'])
def build_flightplan():
     
    json_resp_msg = ""
    msfs_airport_list = []
    # get the list of waypoints from the request
    waypoint_list = request.get_json()

    # user has choosen at least one waypoint
    if waypoint_list:
        csv_filepath = os.path.join("flightsimdiscovery/data", "msfs_airports" + "." + "csv")

        with open(csv_filepath, encoding="utf-8") as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                   
                    line_count += 1
                else:
                    airport_data = {'ICAO': row[0], 'Airport_Name': row[1], 'lat': float(row[5]), 'lon': float(row[4]), 'elev': float(row[3])}
                    line_count += 1
                    msfs_airport_list.append(airport_data)

        first_poi = waypoint_list[0]
        last_poi =waypoint_list[-1]

        departure_airport = get_nearest_airport(msfs_airport_list, first_poi)
        destination_airport = get_nearest_airport(msfs_airport_list, last_poi)

        json_resp_msg = {'dep_airport': departure_airport, 'dest_airport': destination_airport}

    res = make_response(jsonify(json_resp_msg), 200)

    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    return res


@flightplans.route('/flightplans/export_fp_post', methods=['POST'])
def export_fp_post():

    if current_user.is_authenticated:
        user_id = current_user.id

    else:
        user_id = User.query.filter_by(username='anonymous').first().id

    if request.method == 'POST':

        #  Stores users POI preferences from submitted form
        export_fp_details = request.get_json()
        fp_pois = export_fp_details['fp_pois']
        fp_share = export_fp_details['fp_share']
        fp_name = export_fp_details['fp_name']
        fp_altitude = export_fp_details['fp_altitude']

        # update number flown if this flightplan already exists

        updateFlightPlanNumberFlown(fp_name)

        # Store flight plan and waypoints and add default rating (4) if user wants to share
        # do not store flightplan if name is empty, or the waypoints alreay exist for a flight plan
        if fp_share and fp_name and checkUserFlightPlanWaypointsUnique(user_id, fp_pois):

            
            fp = Flightplan(user_id=user_id, name=fp_name, alitude=fp_altitude, number_flown=1)
            db.session.add(fp)
            db.session.flush()

            rating = FP_Ratings(user_id=user_id, flightplan_id=fp.id, rating_score=4)
            db.session.add(rating)

            for fp_poi in fp_pois:
                poi = Pois.query.filter_by(name=fp_poi).first()
                fp_waypoints = Flightplan_Waypoints(user_id=user_id, poi_id=poi.id, flightplan_id=fp.id)
                db.session.add(fp_waypoints)

        # Add/Update Visited table 
        for fp_poi in fp_pois:
            poi = Pois.query.filter_by(name=fp_poi).first()

            if poi:
                
                # check if already visisted
                visited = Visited.query.filter_by(user_id=user_id).filter_by(poi_id=poi.id).first()

                if not visited:
                    
                    visit = Visited(user_id=user_id, poi_id=poi.id)
                    db.session.add(visit)

        db.session.commit()
                       
    return 'Success'    # must leave this here otherwise flask complains nothing returns

   
@flightplans.route("/flightplans/<int:id>/delete", methods=['POST'])
@login_required
def delete_fp(id):

    page = request.args.get('page')

    flightplan = Flightplan.query.filter_by(id=id).first()
    fp_rating = FP_Ratings.query.filter_by(flightplan_id=id).first()
    fp_waypoints = Flightplan_Waypoints.query.filter_by(flightplan_id=id).all()

    if (current_user.username != 'admin'):

        if (flightplan.user_id != current_user.id):
            abort(403)

    db.session.delete(flightplan)
    db.session.delete(fp_rating)

    for fp_waypoint in fp_waypoints:
        db.session.delete(fp_waypoint)

    db.session.commit()

    if page == 'user_flightplans':
        return redirect(url_for('flightplans.user_flight_plans'))
    elif page == 'shared_flightplans':
        return redirect(url_for('admin.shared_flightplans'))
    else:
        return redirect(url_for('main.home'))
                       
    return 'Success'    # must leave this here otherwise flask complains nothing returns

@flightplans.route("/user_flight_plans", defaults={'user_id': None})
@login_required
def user_flight_plans(user_id):

    if user_id:
        if (current_user.username != 'admin'):
            if (user_id != str(current_user.id)):
                abort(403)
    else:
        user_id = current_user.id
        
    # user_pois_with_additional_data = get_user_pois_dict_inc_favorites_visited(user_id, True)

    user_flightplan_data = get_user_flightplans(user_id)

    # return render_template('user_pois.html', user_pois=user_pois_with_additional_data, favorite_pois=favorite_pois, visited_pois=visited_pois, flagged_pois=flagged_pois, user_flightplan_data=user_flightplan_data)
    return render_template('user_flight_plans.html', user_flightplan_data=user_flightplan_data)