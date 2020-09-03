from flightsimdiscovery.models import Ratings

def get_rating(poi_id):

    sum_rating = 0

    ratings = Ratings.query.filter_by(poi_id=poi_id).all()
    number_of_ratings = 0

    for row in ratings:
        sum_rating += int(row.rating_score)
        number_of_ratings += 1

    return '{0:3.1f}'.format(sum_rating/number_of_ratings)