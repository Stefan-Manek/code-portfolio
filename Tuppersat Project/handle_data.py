# Importing standard libraries
import time
from datetime import datetime as dt
# Importing custom libraries
from gps.parse_gga import gps_altitude
import logging
#########################################################


def handle_gps_sensor(label, sensor_dict):
    """Extracts altitude data from gga string stored as 
    data attribute in GpsReceiver object. 
    Example returns:
    >>> ('alt', 121.4)
    """
    return gps_altitude(sensor_dict[label].data)

def handle_temp(label, sensor_dict):
    """Extracts data attribute of temperature sensor and sensor label in tuple.
    Example returns:
    >>> ('temp_int', 13.7)
    """
    return (label, sensor_dict[label].data)

def handle_press(label, sensor_dict):
    """Extracts pressure reading of pressure sensor and sensor label in tuple.
    Example returns:
    >>> ('p_ext', 13.7)
    """
    t, p = sensor_dict[label].data
    return (label, p)

def handle_humidity(label, sensor_dict):
    """Extracts humidity reading from sensor and returns with label in tuple.
    Example returns:
        >>> ('hum', 5480)"""
    return (label, sensor_dict[label].data)


def handle(sensor, sensor_dict):
    """Handles a sensor with specified process, returning in tuple."""
    handle_process = {
        # Sensor  : process
        'gps'     : handle_gps_sensor,
        'temp2'   : handle_temp,
        'p_ext'   : handle_press,
        'hum'     : handle_humidity,
        'ozone'   : handle_humidity
         }
    return handle_process[sensor](sensor, sensor_dict)
    



def gather_data(sensors_dict):
    """Gathers data from all required sensors and 
    returns as , separated string with appropriate formatting"""
    
    #List of labels of all required sensors
    data_sensors = ('gps',
                    'temp2',
                    'p_ext',
                    'hum',
		    'ozone'
                    )
    #Handle all data sensors, returning list of (label, value) tuples
    data_contents = [handle(sensor, sensors_dict) for sensor in sensors_dict
                     if sensor in data_sensors]
    #Defining as dictionary with label : value pairs
    data_dict = dict(data_contents)
    #Defining as comma-separated string with appropriate formatting
    data_string = format_data(data_dict)
    return data_string


def format_data(data_dict):
    """Formats a dictionary of label : value pairs for all data fields
    into comma-separated string with appropriate formatting."""
    #Formats for each data field
    formats = {
        'alt' : '08.02f',
        'temp2': '+08.03f',
        'p_ext': '09.04f',
        'hum': '04.0f',
        'ozone' : '05.0f'
        }
    #List of data as strings in specified format
    data_list = [format(data_dict[key], formats[key]) if data_dict[key] != None
                 else ' ' for key in data_dict]
    #Returns as comma-separated string
    return ','.join([str(i) for i in data_list])

def gather_full_packet(sensors_dict, index):
    """Gathers data from sensors every 5 seconds, creates a data pakcet
    every 20s with current time and index as a header."""
    data = []
    #Gathers data every 5s and creates packet every 20s
    for i in range(4):
        data.append(gather_data(sensors_dict))
        time.sleep(5)
    
    #Header consisting of timestamp and package index
    header = f'{dt.now():%H%M%S},{index:05d}'
    data.insert(0, header)
    #Returns as ';' delineated bytestring
    return ';'.join(data).encode()


class HandleData:
    """Class to collect relevant data from sensors and send via radio
    at frequency of 20s in separate thread."""
    def __init__(self, sensor_dict, radio):
        """Initialisation"""
        
        #Input dictionary with label : sensor object pairs
        self._sensor_dict = sensor_dict
        
        #Placeholder for data
        self._data = None
        
        # Start package index at 1
        self._packet_index = 1
        
        #Define radio object (SatRadio)
        self._radio = radio
        
        #Set up logger
        self._logger = logging.getLogger(__name__)

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()
        
    def setup(self):
        """No setup process required"""
        self._logger.info('Started handle_data process')
        pass
    
    def teardown(self):
        """No teardown process required."""
        self._logger.info('Ended handle_data process')
        pass
    
    def read(self):
        """Gathers data from relevant sensors and returns as bytestring"""
        self._logger.info('Read all data sensors')
        return gather_full_packet(self._sensor_dict,
                                  self._packet_index)
        
    def update(self):
        """Reads sensor data as bytestring and updates to data attribute. 
        Sends pakcet via radio with a frequency of 20s."""
        
        #Read relevant sensor data as bytestring
        self._data = self.read()
        print(self._data)
        
        #Send data pakcet via radio
        self._logger.info('Sent data packets via radio')
        self._radio.send_data_packet(self._data)
        
        #Update package index by 1
        self._packet_index += 1


        
