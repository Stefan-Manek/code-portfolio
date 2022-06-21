from .DFRobot_Ozone import (DFRobot_Ozone_IIC,
                           MEASURE_MODE_AUTOMATIC,
                           OZONE_ADDRESS_3)
import time
import logging


class OzoneSensor:
    """ A class representing an MS5611 pressure / temperature sensor . """
    def __init__ (self, mode, addr, coll_num):
        """ Initialisation . """
        #Sensor I2C address:
        self._addr = addr
        #Sensor I2C mode
        self._mode = mode
        #Collect number (range 1-100)
        self._coll_num = coll_num
        #Sensor measure mode (set to automatic)
        self._measure_mode = MEASURE_MODE_AUTOMATIC
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
            time.sleep(5)
            pass
        
    def read(self):
        """ Read the ozone concentration (ppb) value from the sensor . """
        time.sleep(1)
        return self._ozone_sensor.get_ozone_data(self._coll_num)
    
    def setup(self):
        """ Define ozone sensor object. """
        self._ozone_sensor = DFRobot_Ozone_IIC(self._mode,
                                               self._addr)
        #Set sensor measurement mode
        self._ozone_sensor.set_mode(self._measure_mode)
    
    def teardown (self):
        """ The ozone sensor needs no cleaning up. """
        pass

    @property
    def data(self):
        return self._data
