import click
import uuid
from flask import Blueprint
import wikipedia
from flightsimdiscovery.models import Pois
from flightsimdiscovery import db
from utilities import get_default_airports
from flightsimdiscovery.admin.utilities import update_db, backup_db
from xml.dom import minidom
import xml.etree.ElementTree as ET 
from requests import get
from sqlalchemy.sql.expression import null
from utilities import get_elevation
import csv
import os
from tempfile import NamedTemporaryFile
import shutil
import traceback
from sqlalchemy import or_

scriptsbp = Blueprint('scripts', __name__)

#RUN THE FOLLWOING SCRIPTS IN ORDER AFTER EVERY WORLD UPDATE


# LOCAL ONLY!!! #

# Test world update first as this will add new enhanced aiprots to exclude.  This script determines if
# a default airport should not be shown, due to a POI for this airport already exist.
#
# RUn this script LOCALLY after each update
@scriptsbp.cli.command('update_airports_csv')
def update_airports_csv():

    no_airports_updated = 0
    msfs_airport_list = []
    airport_data = {}
    airports_updated = []
    airports_poi_list = []
        
    csv_filepath = os.path.join("flightsimdiscovery/data", "FSD_airports" + "." + "csv")
    csv_filepath_temp = os.path.join("flightsimdiscovery/data", "FSD_airports_temp" + "." + "csv")
    fields = ['ICAO','Airport_Name','City','Elevation','Longitude','Latitude','tower_frequency','atis_frequency','awos_frequency','asos_frequency','unicom_frequency','Show_on_map']

    with open(csv_filepath, encoding="utf-8") as csv_file:

        csv_reader = csv.DictReader(csv_file, fieldnames=fields, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                
                line_count += 1
            else:
            
                airport_data = {'ICAO': row['ICAO'], 'Airport_Name': row['Airport_Name'], 'City': row['City'], 'Elevation': float(row['Elevation']), 'Longitude': float(row['Longitude']), 'Latitude': float(row['Latitude']), 'tower_frequency': row['tower_frequency'], 'atis_frequency': row['atis_frequency'],'awos_frequency': row['awos_frequency'],'asos_frequency': row['asos_frequency'],'unicom_frequency': row['unicom_frequency'],'Show_on_map': row['Show_on_map']}
                line_count += 1
                msfs_airport_list.append(airport_data)

    exluded_pois = Pois.query.filter(or_(Pois.category == 'Airport (Bush Strip)', Pois.category  == 'Airport (Famous/Interesting)'))

    try:

        for poi in exluded_pois:
            if poi.share == 1:
                airports_poi_list.append(poi.name)
                # poi_name_first_word = poi.name.split()[0]

            # locations are similar.  If so, update csv to not show on map
            location_tolerance = 0.03

            for airport in msfs_airport_list:

                # if (poi.name   == 'Narsarsuaq Airport') and ('Narsarsuaq' in airport['Airport_Name']) :
                #     print('stop')
                    
                latitude_diff = abs(float(poi.latitude) - airport['Latitude'])
                longitude_diff = abs(float(poi.longitude) - airport['Longitude'])

                if (latitude_diff < location_tolerance) and (longitude_diff < location_tolerance):
                    
                    print("Updating CSV to not show airport " + poi.name)  
                    airport['Show_on_map'] = 0
                    no_airports_updated +=1
                    airports_updated.append(poi.name)
        
        #Update csv
        with open(csv_filepath_temp, 'w',encoding="utf-8", newline='') as csv_writer:
            writer = csv.DictWriter(csv_writer, fieldnames=fields)
            writer.writeheader()
            for airport in msfs_airport_list:
                writer.writerow(airport)
                        
    except Exception as e:
        traceback.print_exc()
        print('ERROR running the script!')
      
            
    else:
        shutil.move(csv_filepath_temp, csv_filepath)
        print("Number of airports not showing on map is " + str(no_airports_updated))    
        
        airports_not_updated = (list(set(airports_poi_list) - set(airports_updated)))   
        print("\nAirports not updated:  " + str(len(airports_not_updated))) 
        print(airports_not_updated)
        print('\n')
        print('Script has run succesfully!')

# script to add msfs world update pois to the database.  If multiple countries add 'Region'
@scriptsbp.cli.command('world_update')
@click.argument('xml_filename')
@click.argument('country')
def world_update(xml_filename, country):

    backup_db()
    update_db(xml_filename, country)

# This function generates update any pois with missing elevation.  Best to run this script in the morning.
# You may need to run this script multiple times as opem-elevation api times-out regularly.  
# It also generates an xml file in output that is used by MSFS SDK to build a list of POIs to import into the game
@scriptsbp.cli.command('update_pois_elevation')
def update_pois_elevation():

    msfs_pois = ['MSFS Enhanced Airport', 'MSFS Photogrammetry City', 'MSFS Point of Interest']

    count_pois_no_elevation_retrieved = 0
    
    xml_text = ''
    pois = Pois.query.all()
    root = ET.Element('FSData', version="9.0") 
    tree = ET.ElementTree(root)   

    print("updating elevation of pois")        

    for poi in pois:
        
        share_poi = poi.share
        poi_description = poi.description

        # dont include private pois
        if not share_poi:
            continue

        # dont incluse any msfs pois
        # if any(x in poi_description for x in msfs_pois):
        #     continue

        unique_id =  str(uuid.uuid4())
        poi_lat = str(poi.latitude)
        poi_lng = str(poi.longitude)
        poi_alt = poi.altitude

        # only get elevation if it doesnt alreay exist in the database
        if poi_alt is None:
            try:
                print("TRYING TO GET POI ELEVATION: " + str(poi.id) + "   " + poi.name + " " + poi_lat + "  " + poi_lng)
                poi_alt = get_elevation(poi_lat, poi_lng)
            except Exception as e:  
                print(e)
                continue

            if poi_alt is not None:

                # update database poi with new elevation
                poi_to_update = Pois.query.get_or_404(poi.id)
                poi_to_update.altitude = poi_alt
                db.session.commit()
                print("ADDED POI ELEVATION: " + str(poi.id) + "   " + poi.name + "   " + str(poi_alt))
            else:
                count_pois_no_elevation_retrieved += 1
                
                print(count_pois_no_elevation_retrieved)
        
        landmark_location = ET.SubElement(root, 'LandmarkLocation', instanceId = unique_id, type="POI", name=poi.name, lat=poi_lat, lon=poi_lng, alt=str(poi_alt), offset='0.000000')
    
    
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open('flightsimdiscovery/output/fsd_pois.xml', 'wb') as f:
        f.write(xmlstr.encode('utf-8'))

    print('POIS XML has run succesfully!  Please check the output folder and copy over to the MSFS SDK FSD POIS directory')


# script to add detailed description to msfs pois
@scriptsbp.cli.command('update_msfs_poi_descriptions')
def update_msfs_poi_descriptions():

    no_pois_updated = 0
    no_pois_not_updated = 0
    updated_pois = []


    pois = Pois.query.all()      

    for poi in pois:

        poi_name = ''
        
        # only update poi descriptif it is a new MSFS Point of INterst and hasn't been updated before
        if (poi.description  not in ['MSFS Photogrammery City', 'MSFS Photogrammery City', 'MSFS Point of Interest']):
            continue

        if (poi.description == 'MSFS Photogrammery City'):
            poi.description = 'MSFS Photogrammery City'
            poi_name_list = poi.name.split(',')
            # exlcude county from name as wiki returns county detail rather that the city
            for part_name in poi_name_list:
                if 'County' in part_name:
                    continue
                
                poi_name = poi_name + part_name + ' '

        poi_name = poi_name + ', ' + poi.country
        poi_category = poi.category
        search_name = poi_name + ' ' + poi_category

        try:
            wiki_summary = wikipedia.summary(search_name, sentences=4)

            # wiki search sometimes returns this string for city/town descriptions
            if ('The following is a list of the most populous incorporated places' in wiki_summary):
                continue
            # print(wikipedia.summary(poi_name, sentences=4))
        except wikipedia.exceptions.DisambiguationError:
            print("disamiguation error for poi no. " + str(poi.id))
        except wikipedia.exceptions.PageError:
            print("Page error for poi no. " + str(poi.id) + '  Search was ' + poi_name)
            no_pois_not_updated += 1
        else:

            poi_to_update = Pois.query.get(poi.id)
            poi_to_update.description = 'This is a Microsoft flight simulator enhanced point of interest. ' + wiki_summary
            print('UPdating Poi ' + str(poi.id))
            no_pois_updated += 1
            db.session.commit()
            updated_pois.append(poi_to_update)


# update new enhanced airports/airport POIS with ICAO which is used as a lookup to add coms to the infowindow
@scriptsbp.cli.command('update_icao')
def update_icao():
                
    location_tolerance = 0.03
    no_airports_updated = 0
    airports_updated = []
    default_airports=get_default_airports()
    
    pois = Pois.query.all()      

    for poi in pois:
        if ('Airport' in poi.category) and (not poi.nearest_icao_code):
            
            # look up ICAO from MSFS default airports and update
            for airport in default_airports:

                latitude_diff = abs(float(poi.latitude) - airport['lat'])
                longitude_diff = abs(float(poi.longitude) - airport['lon'])

                if (latitude_diff < location_tolerance) and (longitude_diff < location_tolerance):
                    
                    poi_to_update = Pois.query.get(poi.id)
                    poi_to_update.nearest_icao_code = airport['ICAO']
                    db.session.commit()
                    print("Updating ICAO of airport " + poi.name + "  " + airport['ICAO'])  
                    no_airports_updated +=1
                    airports_updated.append(poi.name)

    print('POIS elevation updated has run succesfully!  Number of pois updated with elevation is ' + str(no_airports_updated))






