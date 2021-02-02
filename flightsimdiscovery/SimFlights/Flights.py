
import os, glob, json
import math
from geopy import Point
from geopy.distance import geodesic
from flightsimdiscovery.SimFlights.DatabaseConnector import FlightDatabase

# Default FLight Variables
flight_path_display_width = 4   # kilometers

class Flights:

    def __init__(self, volanta_flights_path):


        self.json_files = glob.glob(volanta_flights_path + "\*.json")

        print(self.json_files)

        self.flights = []

        for file_path in self.json_files:
            with open(file_path, 'r') as f:

                flight_text = f.read()
                # remove first 3 characters thats added by Volanta's encoding
                flight_data = json.loads(flight_text[3:])
                self.flights.append(flight_data)

    def get_flights(self):

        return self.flights

  