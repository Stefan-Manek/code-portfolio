# Importing standard libraries
import time
from datetime import datetime as dt
# Importing custom libraries
from gps.parse_gga import gga_parser

#########################################################


def handle_gps_sensor(label, sensor_dict):
    """Extracts relevant data from gga string stored as 
    data attribute in GpsReceiver. 
    Example returns:
    >>> [('alt', 121.4),
         ('lat_dec_deg', 53.3096),
         ('lon_dec_deg', -6.2186),
         ('lat_dil' : 1.53)
         ]
    """
    return gga_parser(sensor_dict[label].data)

def handle_temp(label, sensor_dict):
    """Extracts data attribute of temperature sensor and sensor label in tuple.
    Example returns:
    >>> [('temp_int', 13.7)]
    """
    return [(label, sensor_dict[label].data)]

def handle_press(label, sensor_dict):
    """Extracts pressure reading of pressure sensor and sensor label in tuple.
    Example returns:
    >>> [('pressure', 13.7)]
    """
    t, p = sensor_dict[label].data
    return [(label, p)]
    

def handle(sensor, sensor_dict):
    """Handles a sensor with specified process."""
    handle_process = {
        # Sensor  : process
        'gps'     : handle_gps_sensor,
        'temp1'   : handle_temp,
        'temp2'   : handle_temp,
        'pressure': handle_press
         }
    return handle_process[sensor](sensor, sensor_dict)
    

def create_telem_packet(list_of_lists):
    """Concatenates all tuple pairs into single list and
    converts to dictionary object.
    """
    #Combines all (field, value) tuples into  list
    list_of_tuples = sum(list_of_lists, [])
    #Converts list of tuples to dictionary with field : value pairs
    telem_packet = dict(list_of_tuples)
    telem_packet['hhmmss'] = dt.now()
    #Dictionary is in correct format to send using SatRadio
    return telem_packet


def gather_telem_data(sensors_dict):
    """Gathers data from all required sensors and 
    returns as telemtry data dictionary object."""
    #List of sensors required for telemetry data:
    telem_sensors = ('gps',
                     'temp1',
                     'temp2',
                     'pressure')
            
    #List of all required (field, value) tuples from telemetry sensors
    telem_data = [handle(sensor, sensors_dict) for sensor in sensors_dict
                  if sensor in telem_sensors]
    
    #Create telemetry packet as dictionary
    telem_packet = create_telem_packet(telem_data)
    return telem_packet


class HandleTelemetry:
    """Class to collect relevant telemetry data from sensors and 
    send via radio at frequency of 20s in separate thread."""
    def __init__(self, sensor_dict, radio):
        """Initialisation"""
        
        #Input dictionary with label : sensor object pairs
        self._sensor_dict = sensor_dict
        
        #Placeholder data attribute
        self._data = None
        
        #Define radio object (SatRadio)
        self._radio = radio
        
        #Time between packets
        self._pause = 20
        
    def setup(self):
        """No setup process required"""
        pass
    
    def teardown(self):
        """No teardown process required."""
        pass
    
    def read(self):
        """Gathers data from relevant sensors and returns as dictionary"""
        return gather_telem_data(self._sensor_dict)
        
    def update(self):
        """Gathers and creates telemetry packet every 20s and 
        sends using radio"""
        self._data = self.read()
        print(self._data)
        
        #Wait for 20s
        time.sleep(self._pause)
        
        #Send using radio object (SatRadio)
        self._radio.send_telemetry(**self._data)
        
        


        

        
    
