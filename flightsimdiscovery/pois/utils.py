from flightsimdiscovery.models import Ratings, Pois

def get_rating(poi_id):

    rating = 4  # default if error occurs during division
    sum_rating = 0
    ratings = Ratings.query.filter_by(poi_id=poi_id).all()
    number_of_ratings = 0

    for row in ratings:
        sum_rating += int(row.rating_score)
        number_of_ratings += 1
    
    try:
        rating = '{0:3.1f}'.format(sum_rating/number_of_ratings)
    except:
        print('ERROR occured getting rating.  Problably dividing by zero because no rating for the poi exists.  POI is :  '+ str(poi_id))

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
