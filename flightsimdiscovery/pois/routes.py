from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flightsimdiscovery import db
from flightsimdiscovery.pois.forms import PoiCreateForm, PoiUpdateForm
from flightsimdiscovery.models import Pois, User, Ratings
from flask_login import current_user, login_required
from utilities import get_country_region

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
        # Update POIS table
        print('##### SHARE VALUE: ', form.share.data)
        poi = Pois(user_id=user_id, name=form.name.data, latitude=float(form.latitude.data), longitude=float(form.longitude.data),
                   region=get_country_region(form.country.data), country=form.country.data, category=form.category.data,
                   description=form.description.data,
                   nearest_icao_code=form.nearest_airport.data, share=form.share.data)

        db.session.add(poi)
        db.session.commit()

        # Update Rating table - defaul rating when first creating a new POI is 4
        print('Poi ID is: ', poi.id) # This gets the above poi that was just committed.
        rating = Ratings(user_id=user_id, poi_id= poi.id, rating_score=4)
        db.session.add(rating)
        db.session.commit()

        flash('A new point of interest has been created!', 'success')
        return redirect(url_for('main.home', country=poi.country))
    return render_template('create_poi.html', form=form, legend='New Poi')


@pois.route("/poi/<int:poi_id>")
@login_required
def poi(poi_id):
    poi = Pois.query.get_or_404(poi_id)
    return render_template('poi.html', poi=poi)


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
