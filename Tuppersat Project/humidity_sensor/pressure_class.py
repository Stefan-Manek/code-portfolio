from .pressure_utils import read_ms5611, read_calibration_constants
import smbus
import time
import logging


class MS5611ExtSensor:
    """ A class representing an MS5611 pressure / temperature sensor . """
    def __init__ (self, addr):
        """ Initialisation . """
        self._addr = addr
        # the I2C bus
        self._bus = smbus.SMBus(1)
        # placeholder for calibration constants
        self._calibration_constants = None
        # placeholder for data
        self._data = (None, None)
        # defining logger
        self._logger = logging.getLogger(__name__)
        
    def update(self):
        """ Read and update the stored data value . """
        try:
            self._data = self.read()
        except OSError as exc:
            self._logger.exception(type(exc).__name__)
            self._data = (None, None)
            time.sleep(20)
            pass
        
    def read(self):
        """ Read the pressure and temperature values from the sensor . """
        p, t = read_ms5611(
        self._bus,
        self._addr,
        self._calibration_constants)
        return (p ,t)
    
    def setup(self):
        """ Calibrate the MS5611 sensor . """
        try:
            self._calibration_constants = read_calibration_constants(
            self._bus,
            self._addr
            )
        except OSError as exc:
            self._logger.warning(type(exc).__name__)
            self._data = (None, None)
            time.sleep(20)
            pass
    
    def teardown (self):
        """ The MS5611 sensor needs no cleaning up. """
        pass

    @property
    def data(self):
        return self._data

