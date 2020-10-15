from flightsimdiscovery.models import Ratings, Pois

favorite_marker = '/static/img/marker/favorite-marker.png'
visited_marker = '/static/img/marker/visited-marker.png'
user_marker = '/static/img/marker/user-marker.png'
airport_marker = '/static/img/marker/airport-marker.png'
normal_marker = '/static/img/marker/normal-marker.png'

location_exists_diff_default = 0.005

location_exists_cateogry_diff = {

    'default': 0.005,
    'region': 0.1,
    'Landmark: Man-Made':  0.0005,
    'City/Town':  0.01,
    'Megacity/Town':  0.05,
    'National Park':  0.09,
    'Reef':  0.09,
    'River':  0.09
}

def get_rating(poi_id):
    rating = 4  # default if error occurs during division
    sum_rating = 0
    ratings = Ratings.query.filter_by(poi_id=poi_id).all()
    number_of_ratings = 0

    for row in ratings:
        sum_rating += int(row.rating_score)
        number_of_ratings += 1

    try:
        rating = '{0:3.1f}'.format(sum_rating / number_of_ratings)
    except:
        print('ERROR occured getting rating.  Problably dividing by zero because no rating for the poi exists.  POI is :  ' + str(poi_id))

    return rating


def filter_pois_by_category(pois, category):
    filtered_pois = []

    for poi in pois:
        if poi.category == category:
            filtered_pois.append(poi)
    return filtered_pois


def filter_pois_by_region(pois, region):
    filtered_pois = []

    for poi in pois:
        if poi.region == region:
            filtered_pois.append(poi)
    return filtered_pois


def filter_pois_by_country(pois, country):
    filtered_pois = []

    for poi in pois:
        if poi.country == country:
            filtered_pois.append(poi)
    return filtered_pois


def filter_pois_by_rating(pois, rating):
    filtered_pois = []

    for poi in pois:
        poi_rating = float(get_rating(poi.id))

        if poi_rating >= float(rating):
            filtered_pois.append(poi)

    return filtered_pois


def get_marker_icon(poi, user_favorites, user_visited, user_pois):
    if poi.id in user_visited:
        return visited_marker
    elif ('Airport' in poi.category) or ('Bush Strip' in poi.category):
        return airport_marker
    elif poi.id in user_favorites:
        return favorite_marker
    elif poi.id in user_pois:
        return user_marker
    else:
        return normal_marker


def validate_poi_name(name):
    pois = Pois.query.all()
    for poi in pois:
        if poi.name.strip() == name.strip():
            return False

    return True

def poi_name_exists(name):
    pois = Pois.query.filter_by(name=name).first()
    if pois:
            return True
    return False

def location_exists(pois, latitude, longitude, category):
    pois = Pois.query.all()
    location_tolerance = location_exists_cateogry_diff.get(category, location_exists_cateogry_diff['default'])
    for poi in pois:
        latitude_diff = abs(float(poi.latitude) - latitude)
        longitude_diff = abs(float(poi.longitude) - longitude)
        # print(latitude_diff, longitude_diff)
        if (latitude_diff < location_tolerance) and (longitude_diff < location_tolerance):
            return True

    return False


def getTickImageBasedOnState(state):
    if state:
        return "fas fa-check"
    else:
        return ""
