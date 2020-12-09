from flightsimdiscovery.models import Flightplan, Flightplan_Waypoints, Pois

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





