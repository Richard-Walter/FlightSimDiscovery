from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, jsonify, after_this_request
from openpyxl import load_workbook
from flightsimdiscovery import db
from flightsimdiscovery.models import Favorites, Visited
from flask_login import current_user, login_required
from utilities import get_country_region, get_country_list, get_region_list, get_category_list, region_details, countries_details
from flightsimdiscovery.pois.utils import *
from flightsimdiscovery.main.forms import ContactForm
from flightsimdiscovery.users.utitls import send_contact_email

main = Blueprint('main', __name__)


# TODO add logic to validate poi location based on category
# TODO add logic to validate name/location when updating poi

@main.route("/", defaults={'filter_poi_location': None}, methods=['GET', 'POST'])
@main.route("/home", defaults={'filter_poi_location': None}, methods=['GET', 'POST'])
@main.route("/<filter_poi_location>", )
def home(filter_poi_location):
    # test logging
    # print(3/0)
    anchor = ''

    # variables required for google maps to display data
    map_data = []
    map_data_dict = {}
    map_init = {'zoom': 3, 'lat': 23.6, 'long': 170.9}  # centre of map

    # set specific location if coming from a spcific poi link from another page like top ten
    if filter_poi_location:
        location = filter_poi_location.split(", ")
        lat = float(location[0])
        lng = float(location[1])

        map_init = {'zoom': 10, 'lat': lat, 'long': lng}  # centre of poi
        anchor = 'where_togo_area'

    pois = Pois.query.all()
    # user_pois_list = []
    user_pois_dict = {}
    user_pois_list = []
    user_ratings = {}
    user_favorites = []
    user_visited = []
    search_defaults = {'Category': 'Category', 'Region': 'Region', 'Country': 'Country', 'Rating': 'Rating'}
    is_authenticated = False
    user_id = None

    if current_user.is_authenticated:

        is_authenticated = True

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

                map_init['zoom'] = 6  # default country zoom
                map_init['lat'] = countries_details[country][1]
                map_init['long'] = countries_details[country][2]

            elif region != 'Region':
                map_init['zoom'] = region_details[region][2]
                map_init['lat'] = region_details[region][0]
                map_init['long'] = region_details[region][1]

            # Create refined pois list based on search criteria
            if category != 'Category':
                pois = filter_pois_by_category(pois, category)
            if region != 'Region':
                pois = filter_pois_by_region(pois, region)
            if country != 'Country':
                pois = filter_pois_by_country(pois, country)
            if rating != 'Rating':
                pois = filter_pois_by_rating(pois, rating)

            anchor = 'where_togo_area'


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

    # check to see if a new poi has been created.  If so we will zoom to the country level
    country = request.args.get('country', None)
    if country is not None:
        map_init['zoom'] = 6  # default country zoom
        map_init['lat'] = countries_details[country][1]
        map_init['long'] = countries_details[country][2]
        anchor = 'google_map'

    return render_template("home.html", is_authenticated=is_authenticated, user_visited=user_visited,
                           user_favorites=user_favorites, user_ratings=user_ratings, user_pois_json=user_pois_list, pois=map_data, map_init=map_init,
                           search_defaults=search_defaults, categories=get_category_list(), regions=get_region_list(), countries=get_country_list(),
                           _anchor=anchor)
    # return render_template("home.html", pois=data)


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        message = form.message.data
        email = form.email.data
        subject = form.subject.data

        send_contact_email(message, email, subject)

        flash('Thank you for your message.', 'info')
        return redirect(url_for('main.home'))

    return render_template('contact.html', form=form)


@main.route("/build_db")
@login_required
def build_db():
    # open spreadsheet

    workbook = load_workbook(filename="flightsimdiscovery\\output\\poi_database.xlsx")
    sheet = workbook.active
    print("######################")
    print(sheet.cell(row=10, column=3).value)

    print('Building dadtabase')

    if (current_user.username == 'admin') and (True):

        # Test Create
        user_id = 1  # admin will create all these

        for count, row in enumerate(sheet.rows, start=1):
            print(count)
            if count == 1:
                continue  # dont include header

            if row[0].value == "":
                break  # no more data in spreadhseet

            poi = Pois(
                user_id=user_id,
                name=row[0].value, latitude=float(row[2].value),
                longitude=float(row[3].value),
                region=get_country_region(row[4].value),
                country=row[4].value, category=row[1].value,
                description=row[6].value
            )

            db.session.add(poi)
            db.session.commit()

            # Update Rating table
            # print('Poi ID is: ', poi.id) # This gets the above poi that was just committed.
            rating = Ratings(user_id=user_id, poi_id=poi.id, rating_score=4)
            db.session.add(rating)
            db.session.commit()

        flash('Database has been built', 'success')
        return redirect(url_for('main.home'))
    else:

        abort(403)

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

@main.route('/hello', methods=['GET'])
def hello():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    jsonResp = {'jack': 4098, 'sape': 4139}
    print(jsonResp)
    return jsonify(jsonResp)
