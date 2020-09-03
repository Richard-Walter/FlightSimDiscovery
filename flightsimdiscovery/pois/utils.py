from flightsimdiscovery.models import Ratings

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