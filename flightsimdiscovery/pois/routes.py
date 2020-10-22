from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flightsimdiscovery import db
from flightsimdiscovery.pois.forms import PoiCreateForm, PoiUpdateForm
from flightsimdiscovery.models import Pois, User, Ratings, Flagged, Visited, Favorites
from flightsimdiscovery.pois.utils import location_exists, get_rating
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
        # form.country(disabled=True)

    if form.validate_on_submit():

        # check location has not already been used by another poi
        if location_exists(pois, float(form.latitude.data), float(form.longitude.data), form.category.data):
            new_form = PoiUpdateForm()
            new_form.name.data = form.name.data
            new_form.country.data = form.country.data
            new_form.description.data = form.description.data
            new_form.nearest_airport.data = form.nearest_airport.data
            new_form.share.data = form.share.data

            flash('A point of interest already exists at this location', 'danger')
            return render_template('create_poi.html', form=new_form, legend='New Poi')

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
        return redirect(url_for('main.home', _anchor='where_togo_area', pois_created='True', latitude=poi.latitude, longitude=poi.longitude, country=poi.country))

    return render_template('create_poi.html', form=form, share=share_with_community)


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
    poi = Pois.query.get_or_404(poi_id)
    print('current poi ID is ', poi.id)
    print(current_user.username)
    if (current_user.username != 'admin') and (poi.user_id != current_user.id):
        abort(403)

    form = PoiUpdateForm()
    if form.validate_on_submit():

        poi.user_id = current_user.id
        poi.name = form.name.data
        poi.latitude = float(form.latitude.data)
        poi.longitude = float(form.longitude.data)
        poi.region = get_country_region(form.country.data)
        poi.country = form.country.data
        poi.category = form.category.data
        poi.description = form.description.data
        poi.nearest_icao_code = form.nearest_airport.data
        poi.share = form.share.data
        # poi.rating = 5
        db.session.commit()
        flash('Your point of interest has been updated!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.name.data = poi.name
        form.latitude.data = poi.latitude
        form.longitude.data = poi.longitude
        form.category.data = poi.category
        form.country.data = poi.country
        form.description.data = poi.description
        form.nearest_airport.data = poi.nearest_icao_code
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

    if (current_user.username != 'admin'):
        if (poi.user_id != current_user.id):
            abort(403)
    db.session.delete(poi)
    db.session.delete(flagged_poi)

    for visited_poi in visited_poi_list:
        db.session.delete(visited_poi)
    for favorited_pois in favorited_pois_list:
        db.session.delete(favorited_pois)
    for ratings_poi in ratings_poi_list:
        db.session.delete(ratings_poi)

    db.session.commit()
    flash('Your point of interest has been deleted!', 'success')

    if category == 'user_pois':
        return redirect(url_for('users.user_pois'))
    elif category == 'home':
        return redirect(url_for('main.home'))
    else:
        return redirect(url_for('main.home'))

@pois.route("/flag_poi", methods=['POST'])
@login_required
def flag_poi():
    
 
    reason = request.form.get('reason')
    from_page = request.form.get('page')
    poi_id = request.form.get('poi_id')


    if current_user.is_authenticated:

        flagged_pois = poi = Flagged.query.all()

        for flagged_poi in flagged_pois:
            if int(poi_id) == flagged_poi.poi_id:
                return 'Success'    # already flagged
            
        flagged = Flagged(user_id=current_user.id, poi_id=poi_id, reason=reason)
        db.session.add(flagged)
        db.session.commit()

        if from_page == 'user_pois':
            return redirect(url_for('users.user_pois'))
        elif from_page == 'home':
            return 'Success'
        else:
            return 'Success'
    else:
        #  need to be logged in to flag a poi
        abort(403)

@pois.route("/poi/delete_flagged_poi/<poi_id>", methods=['GET', 'POST'])
@login_required
def delete_flagged_poi(poi_id):

    if current_user.is_authenticated and (current_user.username == 'admin'):

        poi = Flagged.query.filter_by(poi_id=poi_id).first()
        db.session.delete(poi)
        db.session.commit()

        return redirect(url_for('admin.flagged_pois'))
    
    else:
        abort(403)