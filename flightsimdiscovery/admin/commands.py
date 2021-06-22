import click
from flask import Blueprint
import wikipedia
from flightsimdiscovery.models import Pois
from flightsimdiscovery import db

scriptsbp = Blueprint('scripts', __name__)

# @scriptsbp.cli.command('test')
# @click.argument('name')
# def create(name):
#     """ Creates a user """
#     print("Create user: {}".format(name))



@scriptsbp.cli.command('update_msfs_poi_descriptions')
# @click.argument('name')
def update_msfs_poi_descriptions():

    no_pois_updated = 0
    no_pois_not_updated = 0


    pois = Pois.query.all()      

    for poi in pois:
        
        # only update poi descriptif it is a new MSFS Point of INterst and hasn't been updated before
        if poi.description != 'MSFS Point of Interest':
            continue

        poi_name = poi.name + ', ' + poi.country
        try:
            wiki_summary = wikipedia.summary(poi_name, sentences=3)
            # print(wikipedia.summary(poi_name, sentences=3))
        except wikipedia.exceptions.DisambiguationError:
            print("disamiguation error for poi no. " + str(poi.id))
        except wikipedia.exceptions.PageError:
            print("Page error for poi no. " + str(poi.id) + '  Search was ' + poi_name)
            no_pois_not_updated += 1
        else:
            poi_to_update = Pois.query.get(poi.id)
            poi_to_update.description = 'MSFS Enhanced Point of Interest.  ' + wiki_summary
            print('UPdating Poi ' + str(poi.id))
            no_pois_updated += 1
            db.session.commit()