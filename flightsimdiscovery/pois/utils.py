from flightsimdiscovery.models import Ratings, Pois

favorite_marker = '/static/img/marker/favorite-marker.png'
favorite_marker_airport = '/static/img/marker/favorite-marker_airport.png'
visited_marker = '/static/img/marker/visited-marker.png'
visited_marker_airport = '/static/img/marker/visited-marker_airport.png'
user_marker = '/static/img/marker/user-marker.png'
user_marker_airport = '/static/img/marker/user-marker_airport.png'
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

        # for photogrametry and msfs places we need to check the description
        if category in ("MSFS Photogrammery City", "MSFS Point of Interest"):
            if category in poi.description:
                filtered_pois.append(poi)
        elif poi.category == category:
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

    is_airport = False

    if ('Airport' in poi.category) or ('Bush Strip' in poi.category):
        is_airport = True
    
    if poi.id in user_pois:
        if is_airport:
            return user_marker_airport
        else:
            return user_marker
    elif poi.id in user_visited:
        if is_airport:
            return visited_marker_airport
        else:
            return visited_marker
    elif poi.id in user_favorites:
        if is_airport:
            return favorite_marker_airport
        else:
            return favorite_marker
    elif is_airport:
        return airport_marker

    else:
        return normal_marker


def validate_poi_name(name):
    pois = Pois.query.all()
    for poi in pois:
        if poi.name.strip().upper() == name.strip().upper():
            return False

    return True

def validate_updated_poi_name(pois, updated_name, updating_poi):
    for poi in pois:
        if poi.id == updating_poi.id:
            continue
        elif poi.name.strip() == updated_name.strip():
            return False

    return True

def poi_name_exists(name):
    pois = Pois.query.filter_by(name=name).first()
    if pois:
            return True
    return False

def location_exists(pois, latitude, longitude, category, updating_poi=None):
    pois = Pois.query.all()
    location_tolerance = location_exists_cateogry_diff.get(category, location_exists_cateogry_diff['default'])
    for poi in pois:
        latitude_diff = abs(float(poi.latitude) - latitude)
        longitude_diff = abs(float(poi.longitude) - longitude)
        # print(latitude_diff, longitude_diff)
        if (latitude_diff < location_tolerance) and (longitude_diff < location_tolerance):
            if updating_poi:
                if poi.id == updating_poi.id:
                    return False    # User can update POI without changing location
                else:
                    return True
            else:
                return True

    return False


def getTickImageBasedOnState(state):
    if state:
        return "fas fa-check"
    else:
        return ""
