import json
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flightsimdiscovery import db
from flightsimdiscovery.pois.forms import PoiCreateForm, PoiUpdateForm
from flightsimdiscovery.models import Pois, User, Ratings, Flagged, Visited, Favorites, FP_Ratings, Flightplan, Flightplan_Waypoints
from flightsimdiscovery.pois.utils import location_exists, get_rating, validate_updated_poi_name
from flask_login import current_user, login_required
from utilities import get_country_region, continents_by_region, get_location_details


pois = Blueprint('pois', __name__)
anonymous_username = 'anonymous'


@pois.route("/poi/new", defaults={'iw_add_poi_location': None}, methods=['GET', 'POST'])
@pois.route("/poi/new/<iw_add_poi_location>", methods=['GET', 'POST'])
@login_required
def new_poi(iw_add_poi_location):
    flag_poi = False
    share_with_community = ""
    pois = Pois.query.all()
    poi_names = [poi.name for poi in pois]
    form = PoiCreateForm()
    lat = ""
    lng = ""

    country = ""
    region = ""

    # get anonymous user
    user_id = User.query.filter_by(username=anonymous_username).first().id  # returns a list 

    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        # lets flag any anonymous created pois for review
        flag_poi = True
        share_with_community = 'style=display:none'   

    # populate lattiude and longitude if coming from Infowindow
    if iw_add_poi_location:
        location = iw_add_poi_location.split(", ")
        lat = location[0]
        lng = location[1]
        location_details = get_location_details(float(lat), float(lng))
        country = location_details.get('country', "")
        print('getting country details', country)
        form.latitude.data = lat
        form.longitude.data = lng
        if country:
            form.country.data = country
            form.country.render_kw = {'disabled': True}
        
        form.latitude.render_kw = {'disabled': True}
        form.longitude.render_kw = {'disabled': True}

    if form.validate_on_submit():

        # check location has not already been used by another poi
        if location_exists(pois, float(form.latitude.data), float(form.longitude.data), form.category.data):
            new_form = PoiCreateForm()
            new_form.name.data = form.name.data
            new_form.country.data = form.country.data
            new_form.description.data = form.description.data
            new_form.nearest_airport.data = form.nearest_airport.data
            new_form.share.data = form.share.data

            flash('A point of interest already exists at this location', 'danger')
            return render_template('create_poi.html', db_poi_names=poi_names, form=new_form, legend='New Poi')

        # determine country from user coordinates not from the country they input in the form
        location_details = get_location_details(float(form.latitude.data), float(form.longitude.data))
        country = location_details.get('country', "")
        if country:
            form.country.data = country

        # Update POIS table
        print('##### SHARE VALUE: ', form.share.data)
        poi = Pois(user_id=user_id, name=form.name.data, latitude=float(form.latitude.data), longitude=float(form.longitude.data),
                   region=get_country_region(form.country.data), country=form.country.data, category=form.category.data,
                   description=form.description.data,
                   nearest_icao_code=form.nearest_airport.data, share=form.share.data, flag=flag_poi)

        db.session.add(poi)
        db.session.commit()

        # Update Rating table - defaul rating when first creating a new POI is 4
        print('Poi ID is: ', poi.id)  # This gets the above poi that was just committed.
        rating = Ratings(user_id=user_id, poi_id=poi.id, rating_score=4)
        db.session.add(rating)
        db.session.commit()

        # flash('A new point of interest has been created!', 'success')
        return redirect(url_for('main.home', _anchor='google_map', pois_created='True', latitude=poi.latitude, longitude=poi.longitude, country=poi.country))

    return render_template('create_poi.html', form=form, db_poi_names=poi_names, share=share_with_community)


@pois.route("/topten_pois/<continent>")
def topten_pois(continent):
    region_pois = []
    poi_ratings = []
    topten_pois = []
    data_table = []

    # get all pois for the continent
    for region in continents_by_region[continent]:
        pois = Pois.query.filter_by(region=region).all()
        region_pois.extend(pois)

    # get poi ratings and order pois by rating hightest to lowest
    for poi in region_pois:
        rating = str(get_rating(poi.id))
        rating_dict = {'poi_id': poi.id, 'rating': rating}
        poi_ratings.append(rating_dict)

    sorted_poi_ratings = sorted(poi_ratings, key=lambda k: k['rating'])

    # get the top ten pois and  dictionary that gets posted for map to use
    for poi_dict in sorted_poi_ratings[-10:]:
        poi = Pois.query.get(poi_dict['poi_id'])

        data_dic = {}
        data_dic['id'] = poi.id
        data_dic['location'] = str(poi.latitude) + ', ' + str(poi.longitude)
        data_dic['name'] = poi.name
        data_dic['category'] = poi.category
        data_dic['country'] = poi.country
        data_dic['description'] = poi.description
        data_dic['rating'] = poi_dict['rating']

        data_table.append(data_dic)

    return render_template('topten_pois.html', pois=data_table, continent=continent)


@pois.route("/poi/<int:poi_id>/update", methods=['GET', 'POST'])
@login_required
def update_poi(poi_id):
    pois = Pois.query.all()
    poi = Pois.query.get_or_404(poi_id)
    print('current poi ID is ', poi.id)
    print(current_user.username)
    if (current_user.id not in [1,3]) and (poi.user_id != current_user.id):
        abort(403)

    form = PoiUpdateForm()

    if form.validate_on_submit():

        flash_error_msg = ''

        if not validate_updated_poi_name(pois, form.name.data, poi):
            flash_error_msg = "A point of interest already exists with the name - " + form.name.data
            
        elif location_exists(pois, float(form.latitude.data), float(form.longitude.data), form.category.data, poi):
            flash_error_msg = "A point of interest already exists at this location"

        if flash_error_msg:
            
            flash(flash_error_msg, 'danger')
            return render_template('update_poi.html', form=form)

        else:
            # determine country from user coordinates not from the country they input in the form
            location_details = get_location_details(float(form.latitude.data), float(form.longitude.data))
            country = location_details.get('country', "")
            current_time = datetime.utcnow
            if country:
                poi.country = country
            else:
                poi.country = form.country.data  # incase lookup failed fall back to user entry

            # poi.user_id = current_user.id
            poi.name = form.name.data
            poi.category = form.category.data
            poi.description = form.description.data        
            poi.latitude = form.latitude.data        
            poi.longitude = form.longitude.data  
            if form.altitude.data:      
                poi.altitude = form.altitude.data        
            poi.share = form.share.data        
            db.session.commit()

            return redirect(url_for('main.home', _anchor='google_map', pois_updated='True', latitude=poi.latitude, longitude=poi.longitude, country=poi.country))

    elif request.method == 'GET':
        form.poi_name.data = poi.name
        form.name.data = poi.name
        form.latitude.data = poi.latitude
        form.longitude.data = poi.longitude
        form.category.data = poi.category
        form.country.data = poi.country
        form.altitude.data = poi.altitude
        form.description.data = poi.description
        # form.nearest_airport.data = poi.nearest_icao_code
        form.share.data = poi.share

    return render_template('update_poi.html', form=form)


@pois.route("/poi/<int:poi_id>/delete", methods=['POST'])
@login_required
def delete_poi(poi_id):
    
    # *** WHEN WE DELETE A POI, WE HAVE DELETE THE CORRESPONDING POI OUT OF THE OTHER TABLES  ****

    category = request.args.get('page')
    poi = Pois.query.get_or_404(poi_id)
    flagged_poi = Flagged.query.filter_by(poi_id=poi_id).first()

    # visited and favorite can contain multuple records for the one poi_id
    visited_poi_list = Visited.query.filter_by(poi_id=poi_id).all()
    favorited_pois_list = Favorites.query.filter_by(poi_id=poi_id).all()
    ratings_poi_list = Ratings.query.filter_by(poi_id=poi_id).all()

    if (current_user.id not in [1,3]) and (poi.user_id != current_user.id):
        abort(403)

    db.session.delete(poi)
    if flagged_poi:
        db.session.delete(flagged_poi)

    for visited_poi in visited_poi_list:
        db.session.delete(visited_poi)
    for favorited_pois in favorited_pois_list:
        db.session.delete(favorited_pois)
    for ratings_poi in ratings_poi_list:
        db.session.delete(ratings_poi)

    # delete record from flight plan tables that contain poi
    fp_id_set = set()
    fp_waypoints_poi_list = Flightplan_Waypoints.query.filter_by(poi_id=poi_id).all()

    for fp_waypoints_poi in fp_waypoints_poi_list:
        fp_id_set.add(fp_waypoints_poi.flightplan_id)

    for fp_id in fp_id_set:
        fp = Flightplan.query.filter_by(id=fp_id).first()
        db.session.delete(fp)

        fp_rating = FP_Ratings.query.filter_by(flightplan_id=fp_id).first()
        db.session.delete(fp_rating)

        fp_waypoints = Flightplan_Waypoints.query.filter_by(flightplan_id=fp_id).all()

        # delete all waypoints associated with the flight plan as the flight plan is no longer valid
        for fp_waypoint in fp_waypoints:
            db.session.delete(fp_waypoint)

    db.session.commit()
    flash('Your point of interest has been deleted!', 'success')

    if category == 'user_pois':
        return redirect(url_for('users.user_pois'))
    elif category == 'home':
        return redirect(url_for('main.home'))
    else:
        return redirect(url_for('main.home'))

@pois.route("/flag_poi", methods=['POST'])
def flag_poi():
    
 
    reason = request.form.get('reason')
    from_page = request.form.get('page')
    poi_id = request.form.get('poi_id')


    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = User.query.filter_by(username='anonymous').first().id  #user is anonymous_username

    flagged_pois = poi = Flagged.query.all()

    for flagged_poi in flagged_pois:
        if int(poi_id) == flagged_poi.poi_id:
            return 'Success'    # already flagged
        
    flagged = Flagged(user_id=user_id, poi_id=poi_id, reason=reason)
    db.session.add(flagged)
    db.session.commit()

    if from_page == 'user_pois':
        return redirect(url_for('users.user_pois'))
    elif from_page == 'home':
        return 'Success'
    else:
        return 'Success'

@pois.route("/poi/delete_flagged_poi/<poi_id>", methods=['GET'])
@login_required
def delete_flagged_poi(poi_id):

    page = request.args.get('page')

    flagged_poi = Flagged.query.filter_by(poi_id=poi_id).first()

    if (current_user.username != 'admin'):

        if (flagged_poi.user_id != current_user.id):
            abort(403)

    db.session.delete(flagged_poi)
    db.session.commit()

    if page == 'user_pois':
        return redirect(url_for('users.user_pois'))
    elif page == 'flagged_pois':
        return redirect(url_for('admin.flagged_pois'))
    else:
        return redirect(url_for('main.home'))

@pois.route("/poi/remove_favorited_poi/<poi_id>", methods=['GET'])
@login_required
def remove_favorited_poi(poi_id):

    page = request.args.get('page')

    favorited_poi = Favorites.query.filter_by(poi_id=poi_id).first()

    if (current_user.username != 'admin'):

        if (favorited_poi.user_id != current_user.id):
            abort(403)

    db.session.delete(favorited_poi)
    db.session.commit()

    if page == 'user_pois':
        return redirect(url_for('users.user_pois'))
    else:
        return redirect(url_for('main.home'))



@pois.route("/poi/remove_visited_poi/<poi_id>", methods=['GET'])
@login_required
def remove_visited_poi(poi_id):

    page = request.args.get('page')

    visited_poi = Visited.query.filter_by(poi_id=poi_id).first()

    if (current_user.username != 'admin'):

        if (visited_poi.user_id != current_user.id):
            abort(403)

    db.session.delete(visited_poi)
    db.session.commit()

    if page == 'user_pois':
        return redirect(url_for('users.user_pois'))
    else:
        return redirect(url_for('main.home'))

