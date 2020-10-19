from flask import render_template, url_for, flash, redirect, request, Blueprint
from flightsimdiscovery import db
from flightsimdiscovery.models import User, Pois
from flask_login import login_user, current_user, logout_user, login_required

admin = Blueprint('admin', __name__)


@admin.route("/flagged_pois", methods=['GET'])
@login_required
def flagged_pois():
    if current_user.is_authenticated and (current_user.username == 'admin'):

        return render_template('admin.html')
    
    else:
        abort(403)
        
@admin.route("/update_database", methods=['GET', 'POST'])
@login_required
def update_database():
    if current_user.is_authenticated and (current_user.username == 'admin'):

        return render_template('admin.html')
    
    else:
        abort(403)
        

@admin.route("/all_pois")
@login_required
def all_pois():
    all_pois_data = []
    if current_user.is_authenticated and (current_user.username == 'admin'):
        
        all_pois = Pois.query.all()
        for poi in all_pois:
            user = User.query.filter_by(id=poi.user_id).first()
            data_location = str(poi.latitude) + ', ' + str(poi.longitude)
            poi_data = {'username': user.username, 'id': poi.id, 'location': data_location, 'name': poi.name, 'date_posted': poi.date_posted, 'category': poi.category,
                             'country': poi.country, 'region': poi.region,'description': poi.description, 'flag': poi.flag}   
            all_pois_data.append(poi_data)       

        return render_template('all_pois.html', all_pois=all_pois_data)
    else:
        return render_template('errors/403.html'), 403


