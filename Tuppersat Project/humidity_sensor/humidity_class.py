from .humidity_utils import read_MS8607
import smbus
import logging
import time


class MS8607Sensor:
    """ A class representing an MS5611 pressure / temperature sensor . """
    def __init__ (self, addr):
        """ Initialisation . """
        self._addr = addr
        # the I2C bus
        self._bus = smbus.SMBus(1)
        # placeholder for data
        self._data = None
        # defining logger
        self._logger = logging.getLogger(__name__)
        
    def update(self):
        """ Read and update the stored data value . """
        try:
            self._data = self.read()
        except OSError as exc:
            self._logger.exception(type(exc).__name__)
            self._data = None
            time.sleep(20)
            pass
        
    def read(self):
        """ Read the pressure and temperature values from the sensor . """
        rh = read_MS8607(
            self._bus,
            self._addr)
        
        return rh
    
    def setup(self):
        """ Calibrate the MS8607 sensor. """
        pass
    
    def teardown (self):
        """ The MS8607 sensor needs no cleaning up. """
        pass

    @property
    def data(self):
        return self._data

