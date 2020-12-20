import os
import sqlite3

FLIGHTID_TABLE_NAME = 'Flights'
FLIGHT_WAYPOINTS_TABLE_NAME = 'FlightSamples'

class FlightDatabase:
    # DATABASE_PATH = `C:\Users\rjwal_000\Downloads\PilotPathRecorder`


    def __init__(self, database_path):

        self.conn = None

        try:

            # Connect to database
            self.conn = sqlite3.connect(database_path)

        except PermissionError:
            print("Database in use")

        except Exception as ex:
            print("Error connecting to database: \n\n" + str(ex))

    def close_database(self):

        self.conn.close()

    def get_all_flights_ids(self):

        sql_query_text = f"SELECT * FROM {FLIGHTID_TABLE_NAME}"

        try:
            with self.conn:

                cur = self.conn.cursor()
                cur.execute(sql_query_text)
                rows = cur.fetchall()

            return rows

        except Exception as ex:

            print('error exexcuting query')

    def get_flight(self, flight_id):

        sql_query_text = f"SELECT * FROM {FLIGHTID_TABLE_NAME} WHERE FlightID={flight_id} "

        try:
            with self.conn:

                cur = self.conn.cursor()
                cur.execute(sql_query_text)
                rows = cur.fetchall()

            return rows

        except Exception as ex:

            print('error exexcuting query')

    def get_flight_datapoints(self, flight_id):

        sql_query_text = f"SELECT * FROM {FLIGHT_WAYPOINTS_TABLE_NAME} WHERE FlightID={flight_id} "

        try:
            with self.conn:

                cur = self.conn.cursor()
                cur.execute(sql_query_text)
                rows = cur.fetchall()

            return rows

        except Exception as ex:

            print('error exexcuting query')
