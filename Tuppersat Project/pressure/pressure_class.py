from pressure_utils import read_ms5611
from pressure_utils import read_calibration_constants
import smbus
import time
import contextlib

@contextlib.contextmanager
def catch_and_suppress(*exc, callback=None):
    """ Context manager to suppress specified exception types."""
    try:
        yield
    except exc as e:
        if callback:
            callback(e)
    return

def run(loop, setup, teardown):
    setup()
    try:
        while True:
            loop()
    finally:
        teardown()

class MS5611Sensor:
    """ A class representing an MS5611 pressure / temperature sensor . """
    def __init__ (self, addr):
        """ Initialisation . """
        self._addr = addr
        # the I2C bus
        self._bus = smbus.SMBus(1)
        # placeholder for calibration constants
        self._calibration_constants = None
        # placeholder for data
        self._data = None
        
    def update(self):
        """ Read and update the stored data value . """
        self._data = self.read()
        
    def read(self):
        """ Read the pressure and temperature values from the sensor . """
        p, t = read_ms5611(
        self._bus,
        self._addr,
        self._calibration_constants)
        return (p ,t)
    
    def setup(self):
        """ Calibrate the MS5611 sensor . """
        self._calibration_constants = read_calibration_constants(
        self._bus,
        self._addr
        )
    
    def teardown (self):
        """ The MS5611 sensor needs no cleaning up. """
        pass

    @property
    def data(self):
        return self._data

#I2C Address of sensor
ADDR = 0x77

def loop(sensor):
    """Loops read and update processes and prints results"""
    def _loop():
        sensor.update()
        print(f"{time.time():.6f} : {sensor._data}")
    return _loop

def main():
    """Sets up sensor, reads and updates data until a KeyboardInterrupt
    is issued and then tearsdown sensor."""
    sensor = MS5611Sensor(ADDR)
    
    try:
        run(loop(sensor), sensor.setup, sensor.teardown)
        
    except KeyboardInterrupt:
        print('Closing')

if __name__ == "__main__":
    main()
