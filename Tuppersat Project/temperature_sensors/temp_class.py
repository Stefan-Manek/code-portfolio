#Importing libraries
import time
from temperature_sensors.temperature_utils import read_ds18b20
import logging


class DS18B20Sensor:
    """Class representing DS18B20 temperature sensor."""
    def __init__(self, path):
        """Initialisation including file path of sensor"""
        
        #Sensor filepath
        self._path = path
        
        #Data attribute placeholder:
        self._data = None
        
        self._logger = logging.getLogger(__name__)
        
    def update(self):
        """Updates data attribute to most recent sensor reading"""
        try:
            self._data = self.read()
        except (FileNotFoundError, IndexError) as exc:
            self._logger.exception(type(exc).__name__)
            self._data = None
            time.sleep(1)
        
        
        
    def read(self):
        """Reads temperature reading from sensor file.
        Returns temperature in degrees Celsius"""
        return read_ds18b20(self._path)
        

    
    def teardown(self):
        """Sensor file requires no teardown method"""
        pass
    
    def setup(self):
        """"Sensor file requires no setup method"""
        pass
    
    @property
    def data(self):
        """Acquire data attribute"""
        return self._data
    
