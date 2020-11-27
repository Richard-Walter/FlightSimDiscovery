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
from flightsimdiscovery.main.forms import ContactForm
from flightsimdiscovery.users.utitls import send_contact_email
from flightsimdiscovery.config import Config
from utilities import get_location_details

main = Blueprint('main', __name__)

# TODO add tours to each POI 
# TODO anon user can flag a poi - DONE

# TODO allow users to upload photo of location
# TODO export flight plan in xplane format

@main.route("/", defaults={'filter_poi_location': None}, methods=['GET', 'POST'])
@main.route("/home", defaults={'filter_poi_location': None}, methods=['GET', 'POST'])
@main.route("/<filter_poi_location>", )
def home(filter_poi_location):

    # test logging
    # print(3/0)
    anchor = ''

    # variables required for google maps to display data
    gm_key = Config.GM_KEY
    map_data = []
    map_data_dict = {}
    map_init = {'zoom': 3, 'lat': 37.02, 'long': 4.54}  # centre of map

    # set specific location if coming from a spcific poi link from another page like top ten
    if filter_poi_location:
        location = filter_poi_location.split(", ")
        lat = float(location[0])
        lng = float(location[1])

        map_init = {'zoom': 10, 'lat': lat, 'long': lng}  # centre of poi
        anchor = 'where_togo_area'

    pois = Pois.query.all()
    poi_names = [poi.name for poi in pois]
    filtered_pois = None
    search_category_selected = False
    pois_found = True
    pois_created = False
    pois_updated = False
    # user_pois_list = []
    user_pois_dict = {}
    user_pois_list = []
    user_ratings = {}
    user_favorites = []
    user_visited = []
    flagged_pois_list = []
    search_defaults = {'Category': 'Category', 'Region': 'Region', 'Country': 'Country', 'Rating': 'Rating'}
    is_authenticated = False
    user_id = None

    if current_user.is_authenticated:

        is_authenticated = True

        if (current_user.username == 'admin'):
            is_admin = True

        # Create a list of Users POIS for the google map info window to use
        user_id = current_user.id
        user_pois = Pois.query.filter_by(user_id=user_id).all()  # returns a list

        for poi in user_pois:
            # rating = str(get_user_rating(poi.id))
            # visited= get_visited(poi.id)
            # favorited = get_favorited(poi.id)

            # user_pois_dict[poi.id] = {'user_rating': rating, 'visited': visited,'favorited': favorited}    
            user_pois_list.append(poi.id)

            #  User ratings
        user_ratings_query = Ratings.query.filter_by(user_id=user_id).all()  # returns a list
        for rating in user_ratings_query:
            rating_score = str((rating.rating_score))
            user_ratings[rating.poi_id] = {'user_rating': rating_score}

            #  User favorites
        user_favorite_query = Favorites.query.filter_by(user_id=user_id).all()  # returns a list
        for favorite in user_favorite_query:
            user_favorites.append(favorite.poi_id)

            #  User visited
        user_visited_query = Visited.query.filter_by(user_id=user_id).all()  # returns a list
        for visit in user_visited_query:
            user_visited.append(visit.poi_id)

    #  flagged pois
    flagged_pois_query = Flagged.query.all()  # returns a list
    for flagged_poi in flagged_pois_query:
        flagged_pois_list.append(flagged_poi.poi_id)

    # check if user has submitted a search or user has updated poi via the infowindow
    if request.method == 'POST':

        anchor = 'where_togo_area'

        if 'search_form_submit' in request.form:

            pois_search_result_list = []
            poi_id_search_result = set()

            category = request.form.get('selectCategory').strip()
            region = request.form.get('selectRegion').strip()
            country = request.form.get('selectCountry').strip()
            rating = request.form.get('selectRating').strip()

            # update search defaults so it shows the last search criteria
            search_defaults['Category'] = category
            search_defaults['Region'] = region
            search_defaults['Country'] = country
            search_defaults['Rating'] = rating

            # Creat the map intit variables
            if country != 'Country':
                
                large_country_list = ['Russian Federation', 'Canada', 'United States of America', 'China', 'Brazil', 'Australia','India', 'Argentina', 'Kazakhstan', 'Algeria', 'Greenland', 'Saudi Arabia', 'Mexico', 'Congo, Democratic Republic of the']
                
                if country in large_country_list:

                    map_init['zoom'] = 5
                else:
                    map_init['zoom'] = 7 # default country zoom
                
                map_init['lat'] = countries_details[country][1]
                map_init['long'] = countries_details[country][2]

            elif region != 'Region':
                map_init['zoom'] = region_details[region][2]
                map_init['lat'] = region_details[region][0]
                map_init['long'] = region_details[region][1]

            # Create refined pois list based on search criteria
            if category != 'Category':
                pois = filter_pois_by_category(pois, category)
                filtered_pois = pois
                search_category_selected = True
                
            if rating != 'Rating':
                pois = filter_pois_by_rating(pois, rating)
                filtered_pois = pois
                search_category_selected = True
            if region != 'Region':
                # pois = filter_pois_by_region(pois, region)
                filtered_pois = pois
                filtered_pois = filter_pois_by_region(filtered_pois, region)
                search_category_selected = True
            if country != 'Country':
                # pois = filter_pois_by_country(pois, country)
                if filtered_pois is None:
                    filtered_pois = pois

                filtered_pois = filter_pois_by_country(filtered_pois, country)
                search_category_selected = True

            if filtered_pois:
                anchor = 'where_togo_area'
            elif search_category_selected:   # search returned no results
                # flash('No Points of Interest found - Search Again', 'warning')
                pois_found = False
                map_init['zoom'] = 3
                # return redirect(url_for('main.home'))


        elif 'show_ony_user_pois_check' in request.form:
            filter_user_pois = request.form.get('show_ony_user_pois_check')

            if filter_user_pois == 'Yes':
                print('filtering user pois')
                search_defaults['filter_user_pois'] = 'Yes'
                pois_id = set(user_pois_list + user_favorites + user_visited)

                for poi in pois[:]:
                    if poi.id not in pois_id:
                        pois.remove(poi)
            else:
                search_defaults['filter_user_pois'] = 'No'

    # create the Point of Interest dictionary that gets posted for map to use
    for poi in pois:
        # print('Poi', poi)
        data_dic = {}
        data_dic['id'] = poi.id
        data_dic['user_id'] = poi.user_id
        data_dic['name'] = poi.name
        data_dic['category'] = poi.category
        data_dic['country'] = poi.country
        data_dic['region'] = poi.region
        data_dic['description'] = poi.description
        data_dic['rating'] = str(get_rating(poi.id))
        # data_dic['icon'] = '/static/img/marker/normal-marker.png'
        data_dic['icon'] = get_marker_icon(poi, user_favorites, user_visited, user_pois_list)
        data_dic['lat'] = format(poi.latitude, '.6f')
        data_dic['lng'] = format(poi.longitude, '.6f')

        map_data.append(data_dic)

    # check to see if a new poi has been created or updated.  If so we will zoom in close to the newly created poi
    country = request.args.get('country', None)
    new_poi_lat = request.args.get('latitude', None)
    new_poi_long = request.args.get('longitude', None)
    pois_created = request.args.get('pois_created', None)
    pois_updated = request.args.get('pois_updated', None)

    if country is not None:
        map_init['zoom'] = 8
        map_init['lat'] = new_poi_lat
        map_init['long'] = new_poi_long
        # map_init['zoom'] = 6
        # map_init['lat'] = countries_details[country][1]
        # map_init['long'] = countries_details[country][2]
        anchor = 'where_togo_area'

    return render_template("home.html", is_authenticated=is_authenticated, gm_key=gm_key, db_poi_names=poi_names, pois_created=pois_created, pois_updated=pois_updated, pois_found=pois_found, user_visited=user_visited,
                           user_favorites=user_favorites, flagged_pois=flagged_pois_list, user_ratings=user_ratings, user_pois_json=user_pois_list, pois=map_data, map_init=map_init,
                           search_defaults=search_defaults, categories=get_category_list(), regions=get_region_list(), countries=get_country_list(),
                           _anchor=anchor)
    # return render_template("home.html", pois=data)

@main.route("/about")
def about():
    pois = Pois.query.all()
    return render_template("about.html", number_pois=len(pois))

@main.route("/faq")
def faq():

    return render_template("faq.html")


@main.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        message = form.message.data
        from_email = form.email.data
        subject = form.subject.data

        send_contact_email(message, from_email, subject)

        flash('Thank you for your message.', 'info')
        return redirect(url_for('main.home'))

    else:
        
        if current_user.is_authenticated:

            # Create a list of Users POIS for the google map info window to use
            user_id = current_user.id
            user = User.query.filter_by(id=user_id).first()  #
            form.email.data = user.email

    return render_template('contact.html', form=form)


@main.route('/iw_post', methods=['POST'])
@login_required
def iw_post():

    if current_user.is_authenticated:

        is_authenticated = True
        user_id = current_user.id

    if request.method == 'POST':

        if 'favoriteChecked' in request.form:

            #  Stores users POI preferences from submitted form
            favorited = request.form.get('favoriteChecked')
            poi_id = request.form.get('poi_id')

            # Add/Update favorites table
            if favorited:
                favorite = Favorites.query.filter_by(user_id=user_id).filter_by(poi_id=poi_id).first()
                print('OLD favorite: ', favorite)

                if favorite:  # record already exists do nothing
                    pass
                else:
                    favorite = Favorites(user_id=user_id, poi_id=poi_id)
                    db.session.add(favorite)
                    db.session.commit()
                    print('NEW favorite: ', favorite)
            else:  # remove record from db if exists
                favorite = Favorites.query.filter_by(user_id=user_id).filter_by(poi_id=poi_id).first()

                if favorite:
                    print('REMOVING favorite: ', favorite)
                    db.session.delete(favorite)
                    db.session.commit()

        elif 'visitedChecked' in request.form:

            #  Stores users POI preferences from submitted form
            visited = request.form.get('visitedChecked')
            poi_id = request.form.get('poi_id')

            # Add/Update Visited table
            if visited:
                visit = Visited.query.filter_by(user_id=user_id).filter_by(poi_id=poi_id).first()
                print('OLD Visited: ', visit)

                if visit:  # record already exists do nothing
                    pass
                else:
                    visit = Visited(user_id=user_id, poi_id=poi_id)
                    db.session.add(visit)
                    db.session.commit()
                    print('NEW Visited: ', visit)
            else:  # remove record from db if exists
                visit = Visited.query.filter_by(user_id=user_id).filter_by(poi_id=poi_id).first()

                if visit:
                    print('REMOVING Visited: ', visit)
                    db.session.delete(visit)
                    db.session.commit()

        elif 'ratingOptions' in request.form:

            #  Stores users POI preferences from submitted form
            rating_score = request.form.get('ratingOptions')
            poi_id = request.form.get('poi_id')

            # Update ratings table
            if rating_score:
                rating = Ratings.query.filter_by(user_id=user_id).filter_by(poi_id=poi_id).first()
                print('\n\n')
                print('OLD RATING: ', rating)
                if rating:  # update rating score

                    rating.rating_score = rating_score
                else:
                    rating = Ratings(user_id=user_id, poi_id=poi_id, rating_score=rating_score)
                    db.session.add(rating)
                db.session.commit()
                print('NEW RATING: ', rating)

    return 'Success'    # must leave this here otherwise flask complains nothing returns


@main.route('/build_flightplan', methods=['GET', 'POST'])
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


@main.route('/export_fp_post', methods=['POST'])
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

        # Store flight plan and waypoints and add default rating (4) if user wants to share
        # do not store flightplan if name is empty
        if fp_share and fp_name:
            fp = Flightplan(user_id=user_id, name=fp_name, alitude=fp_altitude)
            db.session.add(fp)
            db.session.flush()

            rating = FP_Ratings(user_id=user_id, flightplan_id=fp.id, rating_score=4)
            db.session.add(rating)

            for fp_poi in fp_pois:
                poi = Pois.query.filter_by(name=fp_poi).first()
                fp_waypoints = Flightplan_Waypoints(user_id=user_id, poi_id=poi.id, flightplan_id=fp.id)
                db.session.add(fp_waypoints)

        # Add/Update Visited table if user logged in
        if current_user.is_authenticated:
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

@main.route("/admin")
@login_required
def admin():

    if (current_user.username == 'admin'):

        return render_template('admin.html')
    
    else:
        abort(403)
   
