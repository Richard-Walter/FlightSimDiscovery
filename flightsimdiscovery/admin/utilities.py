import csv, os, json
import xml.etree.ElementTree as ET
from copy import deepcopy
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, jsonify, after_this_request, make_response
from openpyxl import load_workbook
from flightsimdiscovery import db
from flightsimdiscovery.models import Favorites, Visited, User, Flagged
from flask_login import current_user, login_required
from utilities import get_country_region, get_country_list, get_region_list, get_category_list, region_details, countries_details, get_nearest_airport
from flightsimdiscovery.pois.utils import *
from flightsimdiscovery.main.forms import ContactForm
from flightsimdiscovery.users.utitls import send_contact_email
from flightsimdiscovery.config import Config, basedir
from utilities import get_location_details

def get_xml_db_update_list():

    file_path_dict = {}

    xml_files = [os.path.abspath(x) for x in os.listdir(os.path.join(basedir, "input\database_updates"))]
    for xml_file in xml_files:
        file_name = os.path.basename(xml_file)
        file_path_dict[os.path.basename(file_name)] = xml_file

    print(file_path_dict)

    return file_path_dict

def update_db(password):

    pois = Pois.query.all()

    if (current_user.username == 'admin'):

        #  ****** CHANGED THIS  *********
        category = 'Japan'



        user_id = current_user.id # admin will create all these POIS
        name = ''
        latitude = ''
        longitude = ''
        country = ''
        description = ''
        country_set = set()
        countries_not_found = []
        regions_not_found = []
        poi_name_exists_list = []
        poi_location_exists_list = []

        # Parse the update db xml file
        tree = ET.parse("flightsimdiscovery\\input\\database\\Japan Update.xml")
        folders= tree.findall('.//Folder')

        for folder in folders:
            if folder.attrib['Name'] == 'Points of Interest':
                description = 'MSFS Point of Interest'
                category = 'Landmark: Man-Made'

            elif folder.attrib['Name'] == 'Photogrammery Cities':
                description = 'MSFS Photogrammery City'
                category = 'City/Town'
            elif folder.attrib['Name'] == 'Airports Standard':
                description = 'MSFS Enhanced Airport'
                category = 'Airport (Famous/Interesting)'
            for placemark in folder:
                for elem in placemark:
                    if elem.tag == 'name':
                        name =  elem.text

                    elif elem.tag == 'Point':
                        cordinate_tag = elem[0].text
                        coordinates_list = cordinate_tag.strip().split(",")
                        longitude = float(coordinates_list[0])
                        latitude = float(coordinates_list[1])
                        location_details = get_location_details(latitude, longitude)
                        city = location_details.get('city', "")
                        country = location_details.get('country', "")
                        state = location_details.get('state', "")
                        county = location_details.get('county', "")   # commented out for country specific msfs updates
                        if country:
                            country_set.add(country)
                            region = get_country_region(country.strip())
                            if not region:
                                regions_not_found.append(country)
                                break
                        else:
                            countries_not_found.append(name + ", " + str(latitude) + ", " + str(longitude))
                            break
                        
                        if category == "City/Town":
                            if county:
                                name += ", " + county
                            if state:
                                name += ", " + state
                        else:
                            if city:
                                name += ", " + city
                            elif county:
                                name += ", " + county
                            elif state:
                                name += ", " + state

                        # check if name exists
                        poi_name_exists_boolean = poi_name_exists(name)
                        if poi_name_exists_boolean:
                            print("*** POI NAME EXISTS: ", name)
                            poi_name_exists_list.append(name)
                            break

                        # check if location exists
                        poi_location_exists = location_exists(pois, latitude,longitude, category)
                        if poi_location_exists:
                            print("*** POI LOCATION EXISTS: ", name)
                            poi_location_exists_list.append(name)
                            break
                        
                        print(name, country)

                        # create the poi
                        poi = Pois(
                            user_id=user_id,
                            name=name.strip(),
                            latitude=latitude,
                            longitude=longitude,
                            region=region,
                            country=country,
                            category=category,
                            description=description
                        )

                        db.session.add(poi)
                        db.session.commit()

                        # Update Rating table with default rating of 4
                        rating = Ratings(user_id=user_id, poi_id=poi.id, rating_score=4)
                        db.session.add(rating)
                        db.session.commit()

    else:

        abort(403)