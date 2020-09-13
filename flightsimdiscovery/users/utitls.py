import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flightsimdiscovery import mail
from flightsimdiscovery.models import User, Pois, Visited, Favorites
from flightsimdiscovery.pois.utils import getTickImageBasedOnState
from flask import current_app



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:\n
    {url_for('reset_token', token=token, _external=True)}
    \n\nIf you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)

def send_contact_email(message, email, subject):
    
    msg = Message('Flight Sim Discovery - ' + subject,
                  sender=email,
                  recipients=["willthisnamedo@gmail.com"])
    msg.body = message
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
    user_pois = Pois.query.filter_by(user_id=user_id).all()
    user_visited_pois = Visited.query.filter_by(user_id=user_id).all()
    user_visited_poi_id_list = get_pois_id_list(user_visited_pois)

    user_favorited_pois = Favorites.query.filter_by(user_id=user_id).all()
    user_favorited_poi_id_list = get_pois_id_list(user_favorited_pois)

    for poi in user_pois:
        new_poi_data = {'id': poi.id,'name': poi.name, 'category': poi.category, 'country': poi.country, 'region': poi.region, 'description': poi.description }
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

        additional_user_pois_data.append(new_poi_data)
        
    return additional_user_pois_data

def get_pois_id_list(poi_id_list):
    
    id_list = []

    for poi_id in poi_id_list:
        id_list.append(poi_id.poi_id)

    return id_list