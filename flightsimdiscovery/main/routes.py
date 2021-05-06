import csv, os, json
import xml.etree.ElementTree as ET
from copy import deepcopy
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, jsonify, after_this_request, make_response, send_from_directory, session
from openpyxl import load_workbook
from flightsimdiscovery import db
from flightsimdiscovery.models import Favorites, Visited, User, Flagged, Flightplan, Flightplan_Waypoints, FP_Ratings
from flask_login import current_user, login_required
from utilities import get_country_region, get_country_list, get_region_list, get_category_list, region_details, countries_details, get_nearest_airport
from flightsimdiscovery.pois.utils import *
from flightsimdiscovery.main.forms import ContactForm
from flightsimdiscovery.users.utitls import send_contact_email, get_user_flights
from flightsimdiscovery.config import Config
from flightsimdiscovery.flightplans.utils import get_user_flightplans

main = Blueprint('main', __name__)

# DONE Bug in MSFS that doesn't display flightpath to waypoints if ATCWaypoint ID > 6 chars for G3X & G1000
# DONE Fix bug where Clicking on Map ICon ina top ten page gives 404

# TODO BUG - BERRY ISLANDS not working cant select country
# TODO add account setting that bypasses banner and goes straight to map
# TODO Add marker for departure-destination airports for sim flights
# TODO export flights with custom waypoint not showing as visited - seems to work locally check next update
# TODO Exported flight plan with custom waypoints not showing Saved Flight Plans
# TODO allow users to upload photo of location
# TODO aadd phtogrammerty as a category

@main.route('/robots.txt')
@main.route('/sitemap.xml')
def static_from_root():

    return send_from_directory("static", "robots.txt")

@main.route("/", defaults={'filter_poi_location': None}, methods=['GET', 'POST'])
@main.route("/home", defaults={'filter_poi_location': None}, methods=['GET', 'POST'])
@main.route("/focus_on_poi/<filter_poi_location>", )
def home(filter_poi_location):

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
    flightsplans_dic= {}
    flightplans_query = Flightplan.query.all()

    poi_names = [poi.name for poi in pois if poi.share==1]
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
    user_flights = []
    flagged_pois_list = []
    search_defaults = {'Category': 'Category', 'Region': 'Region', 'Country': 'Country', 'Rating': 'Rating'}
    show_my_flights = ''
    is_authenticated = False
    user_id = None


    if current_user.is_authenticated:

        is_authenticated = True

        # get and store user sim flights and show if applicable
        user_flights = get_user_flights()
        # session['user_flights'] = user_flights

        if user_flights:
            if session.get('show_my_flights') == 'No':
                show_my_flights = 'No'
            else:
                show_my_flights = 'Yes'
                session['show_my_flights'] = 'Yes'
        else:
            session['show_my_flights'] = 'No'
            show_my_flights = 'No'
            user_flights = None
            

        # Create a list of Users POIS for the google map info window to use
        user_id = current_user.id
        user_pois = Pois.query.filter_by(user_id=user_id).all()  # returns a list

        for poi in user_pois:

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

    else:
        # user is anonymous
        current_user.id = 2

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

        elif 'show_my_flights_check' in request.form:
            print("in show_my_flights_check")
            show_my_flights = request.form.get('show_my_flights_check')

            if show_my_flights == 'Yes':
                session['show_my_flights'] = 'Yes'
                user_flights

            else:
                session['show_my_flights'] = 'No'     

    # create the Point of Interest dictionary that gets posted for map to use
    for poi in pois:


        # Only include private pois if its the users
        if poi.share == 0:
            if current_user.id != poi.user_id:
                continue

        data_dic = {}
        flightplan_ids = []
        poi_flightplans = Flightplan_Waypoints.query.filter_by(poi_id=poi.id).all()
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

        for fp in poi_flightplans:
            flightplan_ids.append(fp.flightplan_id)

        data_dic['fp_id_list'] = flightplan_ids

        map_data.append(data_dic)

    # create the flighplans dictionary for map to use
    for flightplan in flightplans_query:

        fp_waypoint_list = []
        fp_waypoint_query = Flightplan_Waypoints.query.filter_by(flightplan_id=flightplan.id).all()

        for fp_waypoint in fp_waypoint_query:

            # determine the name of the poi
            poi_name = Pois.query.filter_by(id=fp_waypoint.poi_id).first().name
            fp_waypoint_list.append(poi_name)
        
        flightsplan_dic = {}
        flightsplan_dic['user_id'] = flightplan.user_id
        flightsplan_dic['name'] = flightplan.name
        flightsplan_dic['altitude'] = flightplan.alitude
        flightsplan_dic['waypoints_list'] = fp_waypoint_list

        flightsplans_dic[flightplan.id] = flightsplan_dic

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
        anchor = 'where_togo_area'

    #check to see if user wants to view a fliughtplan
    view_flightplan = request.args.get('view_flightplan', 0)
    view_sim_flight = request.args.get('view_sim_flight', 0)

    return render_template("home.html", is_authenticated=is_authenticated, gm_key=gm_key, db_poi_names=poi_names, view_flightplan=view_flightplan, view_sim_flight=view_sim_flight, pois_created=pois_created, pois_updated=pois_updated, pois_found=pois_found, user_visited=user_visited,
                           user_flights=user_flights, user_favorites=user_favorites, flagged_pois=flagged_pois_list, user_ratings=user_ratings, user_pois_json=user_pois_list, pois=map_data, flightsplans_dic=flightsplans_dic, map_init=map_init,
                           search_defaults=search_defaults, show_my_flights=show_my_flights, categories=get_category_list(), regions=get_region_list(), countries=get_country_list(), _anchor=anchor)

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


@main.route("/view_flightplan/<flightplan_id>")
def view_flightplan(flightplan_id):

    return redirect(url_for('main.home', _anchor='google_map', view_flightplan=flightplan_id))

@main.route("/view_sim_flight/<view_simflight_id>")
def view_sim_flight(view_simflight_id):

    return redirect(url_for('main.home', _anchor='google_map', view_sim_flight=view_simflight_id))

