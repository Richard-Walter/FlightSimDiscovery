
import os
import math
from geopy import Point
from geopy.distance import geodesic
from flightsimdiscovery.SimFlights.DatabaseConnector import FlightDatabase

# Default FLight Variables
flight_path_display_width = 4   # kilometers

class Flights:

    def __init__(self, database_path):

        self.users_flight_db = FlightDatabase(database_path)
        self.latitude_list = []
        self.longitude_list = []
        

    def get_flights(self):

        users_sim_flights = self.users_flight_db.get_all_flights_ids()

        user_flights_datapoints = []

        for sim_flight in users_sim_flights:
            
            flight_info = {}
            flight_path_coordinates = []
            flight_id = sim_flight[0]

            flight_datapoints = self.users_flight_db.get_flight_datapoints(flight_id)  # returns a list of tuples e.g[(20, 2, -35.2921968232364, 149.19443248723417, 1880, 637440143770217255)....

            for datapoint in flight_datapoints:
                self.latitude_list.append(datapoint[2])
                self.longitude_list.append(datapoint[3])
                flight_path_coordinates.append({'lat':datapoint[2],'lng':datapoint[3]})

            zipped_coorindates = list(zip(self.latitude_list, self.longitude_list))

            flight_polygon_points = self.get_flight_path_polygon(zipped_coorindates)

            # google maps requires list of lats and lngs of the polygon
            polygon_coords = []  

            for index, point in enumerate(flight_polygon_points, start=1):
                
                lats_lngs_dict = {'lat': point.latitude, 'lng': point.longitude}
                polygon_coords.append(lats_lngs_dict)

            flight_info['flight_id'] = flight_id
            flight_info['flight_name'] = sim_flight[1]
            flight_info['flight_date'] = sim_flight[2]
            flight_info['flight_path_coords'] = flight_path_coordinates
            flight_info['flight_path_polygon_coords'] = polygon_coords

            user_flights_datapoints.append(flight_info)

        return user_flights_datapoints

    # returns a lits of Points that define the flith path polygon
    def get_flight_path_polygon(self, zipped_coorindates):

        polygon_start_coordinates = []
        polygon_end_coordinates = []

        for index, coordinate in enumerate(zipped_coorindates):

            # need to calculate bearing between two points first
            if index < len(zipped_coorindates) - 1:

                bearing = self.calculate_bearing(Point(*zipped_coorindates[index + 1]), Point(*zipped_coorindates[index]))
                perpendicular_bearings = self.calculate_perpendicular_bearings(bearing)
                polygon_start_coordinates.append(self.calculate_coordinates(Point(*coordinate), perpendicular_bearings[1]))  # anticlockwise/start
                polygon_end_coordinates.append(self.calculate_coordinates(Point(*coordinate), perpendicular_bearings[0]))  # clockwise/end

            # calculate bearing of last zipped coordinate in the list 
            else:
                bearing = self.calculate_bearing(Point(*zipped_coorindates[index]), Point(*zipped_coorindates[index-1]))
                perpendicular_bearings = self.calculate_perpendicular_bearings(bearing)
                polygon_start_coordinates.append(self.calculate_coordinates(Point(*coordinate), perpendicular_bearings[1]))  # anticlockwise/start
                polygon_end_coordinates.append(self.calculate_coordinates(Point(*coordinate), perpendicular_bearings[0]))  # clockwise/end

        polygon_end_coordinates.reverse()

        # append the start and end coordinates of the polygon
        flight_polygon = polygon_start_coordinates + polygon_end_coordinates

        return flight_polygon

    def calculate_coordinates(self, point, bearing_degrees):

        new_location = geodesic(kilometers=flight_path_display_width).destination(point, bearing_degrees).format_decimal()
        # print('new location', new_location)
        new_location = new_location.split(',')
        return Point(new_location[0].strip(), new_location[1].strip())

    def calculate_bearing(self, start_point, end_point):

        """
        Calculates the bearing between two points.

        Parameters
        ----------
        start_point: geopy.Point
        end_point: geopy.Point

        Returns
        -------
        point: int
            Bearing in degrees between the start and end points.
        """

        start_lat = math.radians(start_point.latitude)
        start_lng = math.radians(start_point.longitude)
        end_lat = math.radians(end_point.latitude)
        end_lng = math.radians(end_point.longitude)

        d_lng = end_lng - start_lng
        if abs(d_lng) > math.pi:
            if d_lng > 0.0:
                d_lng = -(2.0 * math.pi - d_lng)
            else:
                d_lng = (2.0 * math.pi + d_lng)

        tan_start = math.tan(start_lat / 2.0 + math.pi / 4.0)
        tan_end = math.tan(end_lat / 2.0 + math.pi / 4.0)
        d_phi = math.log(tan_end / tan_start)
        bearing = (math.degrees(math.atan2(d_lng, d_phi)) + 360.0) % 360.0

        # print('bearing', bearing)

        return bearing

    def calculate_perpendicular_bearings(self, bearing):

        clockwise_perpendicular_bearing = (bearing + 90) % 360
        anticlockwise_perpendicular_bearing = (bearing - 90) % 360

        return [anticlockwise_perpendicular_bearing, clockwise_perpendicular_bearing]
