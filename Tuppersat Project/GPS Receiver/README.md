# GPS Receiver

Code to interface with USB GPS receiver to return position and altitude.

gga_parser.py parses a GGA NMEA message from the receiver and returns the desired values in a dictionary.

gps_sensor_class.py implements the receiver as a class, constantly updating its data attribute as required.
