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

def get_pois_greater_than_or_equal_to(pois, search_rating):

    pois_list = []

    for poi in pois:
        poi_rating = float(get_rating(poi.id))

        if poi_rating >= float(search_rating):

            pois_list.append(Pois.query.get(poi.id))

    return pois_list 
