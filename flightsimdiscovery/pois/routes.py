from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flightsimdiscovery import db
from flightsimdiscovery.pois.forms import PoiCreateForm, PoiUpdateForm
from flightsimdiscovery.models import Pois, User, Ratings
from flightsimdiscovery.pois.utils import location_exists, get_rating
from flask_login import current_user, login_required
from utilities import get_country_region, continents_by_region

pois = Blueprint('pois', __name__)
anonymous_username = 'anonymous'


@pois.route("/poi/new", methods=['GET', 'POST'])
def new_poi():
    pois = Pois.query.all()
    form = PoiCreateForm()
    # default user_id is anonymous
    user_id = User.query.filter_by(username=anonymous_username).first().id  # returns a list  # admin for an anonymous user

    if current_user.is_authenticated:
        user_id = current_user.id

    print("User id is:  ", user_id)

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
                   nearest_icao_code=form.nearest_airport.data, share=form.share.data)

        db.session.add(poi)
        db.session.commit()

        # Update Rating table - defaul rating when first creating a new POI is 4
        print('Poi ID is: ', poi.id)  # This gets the above poi that was just committed.
        rating = Ratings(user_id=user_id, poi_id=poi.id, rating_score=4)
        db.session.add(rating)
        db.session.commit()

        flash('A new point of interest has been created!', 'success')
        return redirect(url_for('main.home', country=poi.country))
    return render_template('create_poi.html', form=form)


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
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.name.data = poi.name
        form.latitude.data = poi.latitude
        form.longitude.data = poi.longitude
        form.country.data = poi.country
        form.description.data = poi.description
        form.nearest_airport.data = poi.nearest_icao_code
        form.share.data = poi.share

    return render_template('update_poi.html', form=form)


@pois.route("/poi/<int:poi_id>/delete", methods=['POST'])
@login_required
def delete_poi(poi_id):
    print('delete post poi_id is ', poi_id)
    poi = Pois.query.get_or_404(poi_id)
    if (current_user.username != 'admin'):
        if (poi.user_id != current_user.id):
            abort(403)
    db.session.delete(poi)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))
