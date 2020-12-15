from flightsimdiscovery.models import Flightplan, Flightplan_Waypoints, Pois
from flightsimdiscovery import db

def checkUserFlightPlanWaypointsUnique(user_id, new_fp_pois):

    new_fp_poi_ids = []
    
    
    # create a list of poi ids for the new flight plan as only names are given
    for poi_name in new_fp_pois:

        poi = Pois.query.filter_by(name=poi_name).first()
        new_fp_poi_ids.append(poi.id)

    # lets check the new flight plan list against other flightplans
    flight_plans = Flightplan.query.all()
    for flight_plan in flight_plans:  

        fp_poi_ids = []    
 
        fp_waypoints = Flightplan_Waypoints.query.filter_by(user_id=user_id).filter_by(flightplan_id=flight_plan.id).all()

        for fp_waypoint in fp_waypoints:
            fp_poi_ids.append(fp_waypoint.poi_id)

        if sorted(fp_poi_ids) == sorted(new_fp_poi_ids):
            return False
    
    return True


def updateFlightPlanNumberFlown(fp_name):
    flight_plan = Flightplan.query.filter_by(name=fp_name).first()

    if flight_plan:
        number_of_flights = flight_plan.number_flown
        if number_of_flights is None:
            flight_plan.number_flown = 1
        else:
            flight_plan.number_flown = number_of_flights + 1
        db.session.add(flight_plan)
        db.session.commit()

    
def get_user_flightplans(user_id):

    user_flightplans_query = Flightplan.query.filter_by(user_id=user_id).all()
    flightsplans_list= []

    for flightplan in user_flightplans_query:

        fp_waypoint_list = ""
        fp_waypoint_query = Flightplan_Waypoints.query.filter_by(flightplan_id=flightplan.id).all()

        for fp_waypoint in fp_waypoint_query:

            # determine the name of the poi
            poi_name = Pois.query.filter_by(id=fp_waypoint.poi_id).first().name
            fp_waypoint_list += poi_name + " -> "

        fp_waypoint_list = strip_end(fp_waypoint_list, " -> ")
        
        flightplan_dic = {}
        flightplan_dic['id'] = flightplan.id
        flightplan_dic['user_id'] = flightplan.user_id
        flightplan_dic['name'] = flightplan.name
        flightplan_dic['altitude'] = flightplan.alitude
        flightplan_dic['waypoints_list'] = fp_waypoint_list

        flightsplans_list.append(flightplan_dic)

    return flightsplans_list

def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]



