
import os, glob, json
import math
from geopy import Point
from geopy.distance import geodesic

# from flightsimdiscovery.SimFlights.DatabaseConnector import FlightDatabase

# Default FLight Variables
flight_path_display_width = 4   # kilometers

class Flights:

    def __init__(self, volanta_flights_path):


        self.json_files = glob.glob(volanta_flights_path + "\*.json")

        self.flights = []

        for file_path in self.json_files:
            with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:

                try:
                    flight_text = f.read()
                    # remove first 3 characters thats added by Volanta's encoding
                    # flight_data = json.loads(flight_text[3:])
                    flight_data = json.loads(flight_text)
                    self.flights.append(flight_data)
                except UnicodeDecodeError:
                    print("unicode decode error in file: " + file_path )

    def get_flights(self):

        # only include relevant data to send to front-end
        flights= []

        for flight in self.flights:
            flight_data = {}
            flight_data['Plan'] = flight['Plan']
            flight_data['AircraftTitle'] = flight['AircraftTitle']
            flight_data['AircraftRegistration'] = flight['AircraftRegistration']
            
            flight_origin = flight['Origin']
            flight_destination = flight['Destination']

            if flight_origin:
                flight_data['Origin'] = flight['Origin']['Name'] + ' (' + flight['Origin']['IcaoCode'] + ')' 
            
            if flight_destination:    
                flight_data['Destination'] = flight['Destination']['Name'] + ' (' + flight['Destination']['IcaoCode'] + ')' 
                
            flight_data['Positions'] = flight['Positions']
            flights.append(flight_data)

        return flights

  