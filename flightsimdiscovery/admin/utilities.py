import os, shutil, datetime
import xml.etree.ElementTree as ET
from flask import abort
from flightsimdiscovery import db
from flask_login import current_user
from utilities import get_country_region
from flightsimdiscovery.pois.utils import *
from flightsimdiscovery.config import basedir, support_dir
from utilities import get_location_details


def get_xml_db_update_list():
    file_path_list = []

    xml_files = [os.path.abspath(x) for x in os.listdir(os.path.join(basedir, "input/database_updates"))]
    for xml_file in xml_files:
        file_path_list.append(os.path.basename(xml_file))
        # file_name = os.path.basename(xml_file)
        # file_path_dict[os.path.basename(file_name)] = xml_file

    return file_path_list


def update_db(file_name, country):
    pois = Pois.query.all()

    full_path = "flightsimdiscovery/input/database_updates/" + file_name

    print(os.getcwd())

    # if (current_user.username == 'admin'):

    # user_id = current_user.id  # admin will create all these POIS
    user_id = 1
    name = ''
    latitude = ''
    longitude = ''
    description = ''
    country_set = set()
    countries_not_found = []
    regions_not_found = []
    poi_name_exists_list = []
    poi_location_exists_list = []

    # Parse the update db xml file
    # tree = ET.parse("flightsimdiscovery\\input\\database_updates\\Japan Update.xml")
    tree = ET.parse(full_path)
    folders = tree.findall('.//Folder')

    for folder in folders:
        if folder.attrib['Name'] == 'Points of Interest':
            description = 'MSFS Point of Interest'
            category = 'Landmark: Man-Made'

        # elif folder.attrib['Name'] == 'Photogrammery Cities':
        elif folder.attrib['Name'] == 'Photogrammetry Cities':
            description = 'MSFS Photogrammetry City'
            category = 'City/Town'
        elif folder.attrib['Name'] == 'Airports Standard':
            description = 'MSFS Enhanced Airport'
            category = 'Airport (Famous/Interesting)'
        for placemark in folder:
            for elem in placemark:
                if elem.tag == 'name':
                    name = elem.text

                elif elem.tag == 'Point':
                    cordinate_tag = elem[0].text
                    coordinates_list = cordinate_tag.strip().split(",")
                    longitude = float(coordinates_list[0])
                    latitude = float(coordinates_list[1])
                    location_details = get_location_details(latitude, longitude)
                    city = location_details.get('city', "")
                    country = location_details.get('country', "")         
                    state = location_details.get('state', "")
                    county = location_details.get('county', "")
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
                    poi_location_exists = location_exists(pois, latitude, longitude, category)
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

                    # get the newly create poi id for rating table
                    new_poi = Pois.query.filter_by(name=name).first()

                    # Update Rating table with default rating of 4
                    rating = Ratings(user_id=user_id, poi_id=new_poi.id, rating_score=4)
                    db.session.add(rating)

        db.session.commit()

    # else:

    #     abort(403)


def backup_db():
    now = str(datetime.datetime.now())[:19]
    now = now.replace(":", "_")

    backup_dir = os.path.join(support_dir, "Database Backups")

    # src_dir="C:\\Users\\Asus\\Desktop\\Versand Verwaltung\\fsdiscovery.db"
    src_dir = os.path.join(support_dir, "fsdiscovery.db")

    # dst_dir="C:\\Users\\Asus\\Desktop\\Versand Verwaltung\\fsdiscovery_"+str(now)+".bd"
    dst_dir = os.path.join(backup_dir, "fsdiscovery_" + str(now) + ".db")
    shutil.copy(src_dir, dst_dir)


