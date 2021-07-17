import os
import secrets
from utilities import get_default_airports
from PIL import Image
from datetime import datetime, timedelta
from flask import url_for, session
from flask_mail import Message
from sqlalchemy.sql.expression import false, true
from flightsimdiscovery import mail, db
from flightsimdiscovery.models import Pois, Visited, Favorites, User, Flagged, Flightplan, Flightplan_Waypoints, User_flight_positions, UserFlights
from flightsimdiscovery.pois.utils import getTickImageBasedOnState
from flask import current_app
from flask_login import current_user
from flightsimdiscovery.config import Config
from json.decoder import JSONDecodeError
from math import cos, sin, asin, sqrt, radians, atan2



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@flightsimdiscovery.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:\n
    {url_for('users.reset_token', token=token, _external=True)}
    \n\nIf you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


def send_contact_email(message, from_email, subject):
    print("recipient", Config.MAIL_USERNAME)
    print("from", from_email)
    msg = Message('Flight Sim Discovery: ' + subject,
                  sender=from_email,
                  recipients=[Config.MAIL_USERNAME])
    # msg.html = '<p><strong>REPLY: </strong> ' + from_email + '</p><br><p><strong>USER MESSAGE:</strong> </p><br><p>' + message + '</p>'
    msg.html = '<a href="mailto:' + from_email  + '?subject=' + subject + '&body=' + message + '"><strong>Reply to feedback</strong></a><br><p><strong>USER MESSAGE:</strong> </p><p>' + message + '</p>'
    mail.send(msg)


def save_picture(form_picture):
    # randomize the users profile picture so it doesn't conflict with another user
    random_hex = secrets.token_hex(8)
    # f_name, f_ext = os.path.splitext(form_picture.filename) # This returns file name and file extension.  we just want extension
    _, f_ext = os.path.splitext(form_picture.filename)  # This returns file name and file extension.  we just want extension
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/img/profile_pics', picture_fn)

    # form_picture.save(picture_path)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def get_user_pois_dict_inc_favorites_visited(user_id, tick=False):
    additional_user_pois_data = []
    user_pois = None

    user = User.query.filter_by(id=user_id).first()
    user_pois = Pois.query.filter_by(user_id=user_id).all()

    user_visited_pois = Visited.query.filter_by(user_id=user_id).all()
    user_visited_poi_id_list = get_pois_id_list(user_visited_pois)

    user_favorited_pois = Favorites.query.filter_by(user_id=user_id).all()
    user_favorited_poi_id_list = get_pois_id_list(user_favorited_pois)

    for poi in user_pois:
        new_poi_data = {'username': user.username, 'id': poi.id, 'name': poi.name, 'date_posted': poi.date_posted, 'category': poi.category, 'country': poi.country, 'region': poi.region,
                        'description': poi.description, 'flag': poi.flag}
        # add location info for map icon in user pois
        new_poi_data['location'] = str(poi.latitude) + ', ' + str(poi.longitude)
        if poi.id in user_visited_poi_id_list:
            if tick:
                new_poi_data['visited'] = getTickImageBasedOnState(True)
            else:
                new_poi_data['visited'] = True
        else:
            if tick:
                new_poi_data['visited'] = getTickImageBasedOnState(False)
            else:
                new_poi_data['visited'] = False

        if poi.id in user_favorited_poi_id_list:
            if tick:
                new_poi_data['favorited'] = getTickImageBasedOnState(True)
            else:
                new_poi_data['favorited'] = True
        else:
            if tick:
                new_poi_data['favorited'] = getTickImageBasedOnState(False)
            else:
                new_poi_data['favorited'] = False

        if poi.share:
            if tick:
                new_poi_data['share'] = getTickImageBasedOnState(True)

        additional_user_pois_data.append(new_poi_data)

    return additional_user_pois_data


def get_pois_id_list(poi_id_list):
    id_list = []

    for poi_id in poi_id_list:
        id_list.append(poi_id.poi_id)

    return id_list

def get_user_favorited_pois(user_id):

    additional_user_pois_data = []

    user_favorited_pois = Favorites.query.filter_by(user_id=user_id).all()
    user_favorited_poi_id_list = get_pois_id_list(user_favorited_pois)

    for poi_id in user_favorited_poi_id_list:
        poi = Pois.query.filter_by(id=poi_id).first()
        poi_data = {'id': poi.id, 'name': poi.name,'category': poi.category, 'country': poi.country, 'description': poi.description}
        # add location info for map icon in user pois
        poi_data['location'] = str(poi.latitude) + ', ' + str(poi.longitude)

        additional_user_pois_data.append(poi_data)

    return additional_user_pois_data

def get_user_visited_pois(user_id):

    additional_user_pois_data = []

    user_visited_pois = Visited.query.filter_by(user_id=user_id).all()
    user_visited_poi_id_list = get_pois_id_list(user_visited_pois)

    for poi_id in user_visited_poi_id_list:
        poi = Pois.query.filter_by(id=poi_id).first()
        poi_data = {'id': poi.id, 'name': poi.name, 'date_posted': poi.date_posted, 'category': poi.category, 'country': poi.country, 'description': poi.description}
        # add location info for map icon in user pois
        poi_data['location'] = str(poi.latitude) + ', ' + str(poi.longitude)

        additional_user_pois_data.append(poi_data)

    return additional_user_pois_data


def get_user_flagged_pois(user_id):

    additional_user_pois_data = []

    user_flagged_pois = Flagged.query.filter_by(user_id=user_id).all()

    for user_flagged_poi in user_flagged_pois:
        poi = Pois.query.filter_by(id=user_flagged_poi.poi_id).first()
        poi_data = {'id': poi.id, 'name': poi.name, 'reason': user_flagged_poi.reason}
        # add location info for map icon in user pois
        poi_data['location'] = str(poi.latitude) + ', ' + str(poi.longitude)

        additional_user_pois_data.append(poi_data)

    return additional_user_pois_data

def save_flight_data_to_db(recorded_flight):

    flight_details = recorded_flight['recorded_flight_details']
    flight_positions = recorded_flight['recorded_flight_positions']

    start_position = flight_positions[0]
    start_time_ms = start_position['last_update_ms']
    end_position = flight_positions[-1]
    end__time_ms = end_position['last_update_ms']
    flight_date = getDatetimeFromMilliSec(start_time_ms)
    real_flight_time = round(((end__time_ms - start_time_ms)/1000), 5)

    aircraft_title = flight_details['aircraft_name']
    aircraft_reg = flight_details['aircraft_rego']
    
    # get origin and destination airports if there are any
    origin_airport_details = getFlightAirportFromPosition(start_position)
    destination_airport_details = getFlightAirportFromPosition(end_position)

    origin_airport_name = origin_airport_details['name']
    origin_airport_icao = origin_airport_details['icao']
    destination_airport_name = destination_airport_details['name']
    destination_airport_icao = destination_airport_details['icao']


    user_flight_db = UserFlights(user_id=current_user.id, aircraft_title=aircraft_title, aircraft_reg=aircraft_reg,
                            origin_name=origin_airport_name, origin_icao=origin_airport_icao, destination_name=destination_airport_name, destination_icao=destination_airport_icao,
                            flight_date=flight_date, real_flight_time=real_flight_time)

    db.session.add(user_flight_db)
    db.session.flush()

    # create flight lat-lng positions
    for index, position in enumerate(flight_positions):

        # only store every 4th position and the last position
        if (index % 4 == 0) or (index == (len(flight_positions)-1)):

            # only store if aircraft is moving uness it is the first and last position
            if (position['ground_speed'] != 0) or (index==0) or (index == (len(flight_positions)-1)):
            
                latitude = position['user_lat']
                longitude = position['user_lng']
                altitude = position['altitude']
                altitude_agl = position['altitude_agl']
                flight_positions_db = User_flight_positions(flight_id=user_flight_db.flight_id,latitude=latitude, longitude=longitude,altitude=altitude, altitude_agl=altitude_agl)

                db.session.add(flight_positions_db)
                
    try:
        db.session.commit()
    except Exception:
        raise JSONDecodeError
    else:
        # assume user wants to see his flights after uploading
        session['show_my_flights'] = 'Yes'

# def save_flight_data_to_db(json_flight_data, flight_recorder):

    
#     for flight in json_flight_data:

#         aircraft_title = ""
#         aircraft_reg = ""
#         origin_name = ""
#         origin_icao = ""
#         destination_name = ""
#         destination_icao = ""
#         flight_date = None
#         network = ""

#         flight_positions = []
#         flight_data = {}
#         filename = flight['Id']
#         flight_state = flight['State']
#         real_flight_time_sec = flight['RealFlightTime']
        

#         # check if flight already exists or was cancelled.  Ignore if so.  Assumes filename is unique
#         if get_flight(filename) or (flight_state == 'Cancelled') or (not real_flight_time_sec):
#             continue
        
#         aircraft_title = flight['AircraftTitle']
#         aircraft_reg = flight['AircraftRegistration']

#         if flight['Origin']:
#             origin_name = flight['Origin'].get('Name')
#             origin_icao = flight['Origin'].get('IcaoCode')
#         if flight['Destination']:
#             destination_name = flight['Destination'].get('Name')
#             destination_icao = flight['Destination'].get('IcaoCode')
#         network = flight['Network']
        
#         flight_date_str = flight['OffBlocksTime']
        
#         try:
#             flight_date = datetime.strptime(flight_date_str, r"%Y-%m-%dT%H:%M:%S.%f")   #e.g. "2021-02-12T02:46:22.372",
#         except (ValueError, TypeError) as e:
#             print('strtime error' , e, 'filename is ', filename)
#             # just use current date by defaul
#             # flight_date = datetime.utcnow
#             pass

#         user_flight_db = UserFlights(user_id=current_user.id, filename=filename, aircraft_title=aircraft_title, aircraft_reg=aircraft_reg,
#                                 origin_name=origin_name, origin_icao=origin_icao, destination_name=destination_name, destination_icao=destination_icao,
#                                 network=network, flight_date=flight_date, real_flight_time=real_flight_time_sec)
 
#         db.session.add(user_flight_db)
#         db.session.flush()

#         # create flight lat-lng positions
#         positions = flight['Positions']
#         for index, position in enumerate(positions):
#             # only get every 4th position and the last position
#             if (index % 4 == 0) or (index == (len(positions)-1)):
#                 latitude = position['Latitude']
#                 longitude = position['Longitude']
#                 altitude = position['Altitude']
#                 altitude_agl = position['AltitudeAgl']
#                 altitude_agl = position['AltitudeAgl']
#                 on_ground = position['OnGround']
#                 OnGround = 1 if position['OnGround'] == True else 0
#                 flight_positions_db = User_flight_positions(flight_id=user_flight_db.flight_id,latitude=latitude, longitude=longitude,altitude=altitude, altitude_agl=altitude_agl, OnGround=OnGround)

#                 db.session.add(flight_positions_db)
            

#     try:
#         db.session.commit()
#     except Exception:
#         raise JSONDecodeError
#     else:
#         # assume user wants to see his flights after uploading
#         session['show_my_flights'] = 'Yes'

def get_flight(filename):

    return UserFlights.query.filter_by(filename=filename).first()

def get_user_flights():

    try:

        user_flights = UserFlights.query.filter_by(user_id=current_user.id).all()

        flights= []
        
        for flight in user_flights:

            # dont show flight if it has been flagged as not show.  THis happens when user deletes a flight
            if flight.show_flight is False:
                continue
            
            flight_positions = []
            flight_data = {}
            flight_data['Flight_ID'] = flight.flight_id
            flight_data['Date'] = (flight.flight_date).strftime("%d-%b-%Y %H:%M")
            flight_time_sec = float(flight.real_flight_time)
            flight_data['Flight_time'] = str(timedelta(seconds=round(flight_time_sec)))
            flight_data['AircraftTitle'] = flight.aircraft_title
            flight_data['AircraftRegistration'] = flight.aircraft_reg
            flight_data['Filename'] = flight.filename
            flight_origin_name = flight.origin_name
            flight_origin_icao = flight.origin_icao
            flight_destination_name = flight.destination_name
            flight_destination_icao = flight.destination_icao

            if flight_origin_name:
                flight_data['Origin_name'] = flight_origin_name
                flight_data['Origin_icao'] = flight_origin_icao
            
            if flight_destination_name:    
                flight_data['Destination_name'] = flight_destination_name
                flight_data['Destination_icao'] = flight_destination_icao

            # create flight lat-lng positions
            positions = User_flight_positions.query.filter_by(flight_id=flight.flight_id).all()
            for position in positions:
                flight_positions.append({'Latitude': position.latitude, 'Longitude': position.longitude, 'Altitude': position.altitude})

            flight_data['Positions'] = flight_positions

            flights.append(flight_data)

    except Exception as e:
        print(e)
        print("Something went wrong getting users flights")
        #dont crash app if something goies wrong with getting user flights
        
    else:
        return flights

def msfs_encrypt(num):

    times_number = num*34
    return 'rjw' + str(times_number)

def msfs_decrypt(string_num_rep):

    times_number  = int(string_num_rep[3:])
    return int(times_number/34)

def getDatetimeFromMilliSec(unix_date):

    flight_date = ''

    try:
        # flight_date = datetime.strptime(flight_date_str, r"%Y-%m-%dT%H:%M:%S.%f")   #e.g. "2021-02-12T02:46:22.372",
        flight_date = datetime.utcfromtimestamp(unix_date/1000)   #e.g. "1626268350040",
        # flight_date = flight_date_unformatted.strftime(r"%Y-%m-%dT%H:%M:%S.%f")  #e.g. "1626268350040",
    except (Exception) as e:
        print('strtime error')
        print(e)
        #just use current date by default
        flight_date = datetime.utcnow().strftime(r"%Y-%m-%dT%H:%M:%S.%f")
    finally:
        return flight_date

def getFlightAirportFromPosition(position):

    # buffer used to determine if user is near closest airport (km)
    default_airports = get_default_airports()
    buffer = 5
    airport_details = {'name': 'Unknown','icao': 'Unknown' }

    def distance_between_points(lat1, lon1, lat2, lon2):
        p = 0.017453292519943295    #Math.PI / 180
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a))
        # R = 6373.0
        # lat1 = radians(lat1)
        # lon1 = radians(lon1)
        # lat2 = radians(lat2)
        # lon2 = radians(lon2)
        # dlon = lon2 - lon1
        # dlat = lat2 - lat1
        # a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        # c = 2 * atan2(sqrt(a), sqrt(1 - a))
        # distance = R * c

        # return distance

    nearest_airport = min(default_airports, key=lambda p: distance_between_points(p['lat'], p['lon'], position['user_lat'], position['user_lng']))   

    # Check if users location is near the vicinity of the airport 
    distance_airport_to_position = distance_between_points(nearest_airport['lat'],nearest_airport['lon'], position['user_lat'], position['user_lng'])
    if distance_airport_to_position < buffer:  
        airport_details['name'] = nearest_airport['Airport_Name']
        airport_details['icao'] = nearest_airport['ICAO']

    return airport_details
    

