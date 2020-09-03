import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from openpyxl import load_workbook
from flightsimdiscovery import db
from flightsimdiscovery.models import Pois, Ratings, Favorites, Visited
from flask_login import current_user, login_required
from utilities import get_country_region, get_country_list, get_region_list, get_category_list, region_details, countries_details
from flightsimdiscovery.pois.utils import get_rating

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    # variables required for google maps to display data
    map_data = []
    map_data_dict = {}
    map_init = {'zoom': 3, 'lat': 23.6, 'long': 170.9}  # centre of map
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

            # check if user has submitted a search and filter database
    if request.method == 'POST':

        if 'search_form_submit' in request.form:

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

            # pois = Pois.query.filter_by(region='Oceania')
            if category != 'Category':
                pois = Pois.query.filter_by(category=category)
            if region != 'Region':
                pois = Pois.query.filter_by(region=region)
            if country != 'Country':
                pois = Pois.query.filter_by(country=country)
            if rating != 'Rating':
                pois = Pois.query.filter_by(rating=rating)

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

        elif 'favoriteChecked' in request.form:

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

            # return   # dont wont to reload the page, just store the users settg

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
        data_dic['rating'] = '4'   # give new poi a default rating of 4
        data_dic['icon'] = '/static/img/marker/map-mark.png'
        data_dic['lat'] = poi.latitude
        data_dic['lng'] = poi.longitude

        map_data.append(data_dic)

    return render_template("home.html", _anchor="where_togo_area", is_authenticated=is_authenticated, user_visited=user_visited,
                           user_favorites=user_favorites, user_ratings=user_ratings, user_pois_json=user_pois_list, pois=map_data, map_init=map_init,
                           search_defaults=search_defaults, categories=get_category_list(), regions=get_region_list(), countries=get_country_list())
    # return render_template("home.html", pois=data)


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/contact")
def contact():
    return render_template("contact.html")


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
