#Importing standard libraries
from threading import Event

#Importing custom libraries
import thread_utils as tu


############################################################

class RunSensors:
    """Class to run all sensors as threads"""
    def __init__(self, sensor_dict):
        """Initialisation"""
        
        self._sensor_list = sensor_dict.values()
        
        self._stop_event = Event()
        
        #List of threads for all sensors:
        self._threads = [tu.sensor_thread(sensor, self._stop_event)
                         for sensor in self._sensor_list]
        
        
    def __enter__(self):
        self.setup()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()
        
    def setup(self):
        """Setup by starting all sensor threads"""
        tu.start_threads(self._threads)
    
    def teardown(self):
        """Teardown by stopping all threads"""
        tu.stop_threads(self._stop_event, self._threads)
        
    def loop(self):
        """No loop method required"""
        pass