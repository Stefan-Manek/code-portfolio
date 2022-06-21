from tuppersat_utils.fileutils import OutputFile
from datetime import datetime as dt
import time
import logging

def timestamp(datetime=None, fmt='%H%M%S'):
    if datetime is None:
        datetime = dt.now()
    return f'{datetime:{fmt}}'

#Sensor groups
GROUPS = {'gps' : ['gps'],
          'interior': ['temp1', 'pressure'],
          'payload' : ['temp2', 'p_ext', 'hum', 'ozone']}

def collect_data(sensor_dict):
    """For each group gathers all relevant data in list.
    Returns dictionary with group : data list pairs"""
    return{group: [sensor_dict[sensor].data for sensor in sensors] for
           (group,sensors) in GROUPS.items()}

####################################################

        
def data_to_string(data_list):
    """Places contents of list in comma-separated string
    with timestamp."""
    data_list.insert(0, f"{dt.now():%H%M%S}")
    return ','.join([str(i) for i in data_list])

#####################################################

DATA_DIR = '/home/pi/flight_data/'

class StoreData:
    """Class to collect all data from sensors and save to local file."""
    def __init__(self, sensor_dict):
        """Initialisation"""
        
        #Input dictionary with label : sensor object pairs
        self._sensor_dict = sensor_dict
        
        #Placeholder for data
        self._data = None
        
        #Time between updates
        self._pause = 1
        
        
        #Dictionary of group:filename pairs
        _time = timestamp()
        self._filenames = {
            'gps' : f'{DATA_DIR}{_time}_gps.txt',
            'interior' : f'{DATA_DIR}{_time}_internal.txt',
            'payload' : f'{DATA_DIR}{_time}_payload.txt'}
        
        #Setup logger
        self._logger = logging.getLogger(__name__)

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()

    
    def setup(self):
        """Create and open all files"""
        self._files = {k: OutputFile(v) for (k,v) in self._filenames.items()}
        for file in self._files.values(): file.open()
        #Log action
        self._logger.info('Created data files')
        
    def teardown(self):
        """Close all files"""
        #Log action
        for file in self._files.values(): file.close()
        self._logger.info('Closed data files')
    
    def read(self):
        """Gathers data from all sensors and returns as 
        comma-separated string"""
        return collect_data(self._sensor_dict)
        


        
    def update(self):
        """Reads sensor data as bytestring and updates to data attribute. 
        Sends pakcet via radio with a frequency of 20s."""
        
        #Read sensor data as string
        self._data = self.read()
        
        #Write data from each sensor group to individual file
        for group in self._data: 
            self._files[group].writeline(data_to_string(self._data[group]))
            
        #Pause between readings
        time.sleep(self._pause)

