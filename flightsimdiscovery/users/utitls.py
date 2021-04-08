import os
import secrets
from PIL import Image
from datetime import datetime
from flask import url_for
from flask_mail import Message
from flightsimdiscovery import mail, db
from flightsimdiscovery.models import Pois, Visited, Favorites, User, Flagged, Flightplan, Flightplan_Waypoints, User_flight_positions, UserFlights
from flightsimdiscovery.pois.utils import getTickImageBasedOnState
from flask import current_app
from flask_login import current_user
from flightsimdiscovery.config import Config
from json.decoder import JSONDecodeError


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

def save_flight_data_to_db(json_flight_data, flight_recorder):


    for flight in json_flight_data:

        aircraft_title = ""
        aircraft_reg = ""
        origin_name = ""
        origin_icao = ""
        destination_name = ""
        destination_icao = ""
        flight_date = None
        network = ""

        flight_positions = []
        flight_data = {}
        filename = flight['Id']
        flight_state = flight['State']
        

        # check if flight already exists or was cancelled.  Ignore if so.  Assumes filename is unique
        if get_flight(filename) or (flight_state == 'Cancelled'):
            continue
        
        aircraft_title = flight['AircraftTitle']
        aircraft_reg = flight['AircraftRegistration']

        if flight['Origin']:
            origin_name = flight['Origin'].get('Name')
            origin_icao = flight['Origin'].get('IcaoCode')
        if flight['Destination']:
            destination_name = flight['Destination'].get('Name')
            destination_icao = flight['Destination'].get('IcaoCode')
        network = flight['Network']
        flight_date_str = flight['OffBlocksTime']
        
        try:
            flight_date = datetime.strptime(flight_date_str, r"%Y-%m-%dT%H:%M:%S.%f")   #e.g. "2021-02-12T02:46:22.372",
        except (ValueError, TypeError):
            print('strtime error' , 'filename is ', filename)
            # just use current date by defaul
            # flight_date = datetime.utcnow
            pass

        user_flight_db = UserFlights(user_id=current_user.id, filename=filename, aircraft_title=aircraft_title, aircraft_reg=aircraft_reg,
                                origin_name=origin_name, origin_icao=origin_icao, destination_name=destination_name, destination_icao=destination_icao,
                                network=network, flight_date=flight_date)
 
        db.session.add(user_flight_db)
        db.session.flush()

        # create flight lat-lng positions
        positions = flight['Positions']
        for position in positions:
            latitude = position['Latitude']
            longitude = position['Longitude']
            altitude = position['Altitude']
            altitude_agl = position['AltitudeAgl']
            altitude_agl = position['AltitudeAgl']
            on_ground = position['OnGround']
            OnGround = 1 if position['OnGround'] == True else 0
            flight_positions_db = User_flight_positions(flight_id=user_flight_db.flight_id,latitude=latitude, longitude=longitude,altitude=altitude, altitude_agl=altitude_agl, OnGround=OnGround)

            db.session.add(flight_positions_db)

       

    try:
        db.session.commit()
    except Exception:
        raise JSONDecodeError

def get_flight(filename):

    return UserFlights.query.filter_by(filename=filename).first()

def get_user_flights():

    

    try:

        user_flights = UserFlights.query.filter_by(user_id=current_user.id).all()

        flights= []
        
        for flight in user_flights:
            flight_positions = []
            flight_data = {}
            flight_data['Flight_ID'] = flight.flight_id
            flight_data['AircraftTitle'] = flight.aircraft_title
            flight_data['AircraftRegistration'] = flight.aircraft_reg
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
