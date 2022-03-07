from temperature_utils import read_ds18b20
import time
import contextlib

def run(loop, setup, teardown):
    setup()
    try:
        while True:
            loop()
    finally:
        teardown()
        
        
@contextlib.contextmanager
def catch_and_suppress(*exc, callback=None):
    """ Context manager to suppress specified exception types."""
    try:
        yield
    except exc as e:
        if callback:
            callback(e)
    return
        

class DS18B20Sensor:
    def __init__(self, path):
        self._path = path
        
        self._data = None
        
    def update(self):
        self._data = self.read()
        
    def read(self):
        t_degC = read_ds18b20(self._path)
        return t_degC
    
    def teardown(self):
        pass
    
    def setup(self):
        pass
    
    @property
    def data(self):
        return self._data
    


PATH = '/sys/bus/w1/devices/28-00000deac472/w1_slave'

def loop(sensor):
    def _loop():
        sensor.update()
        print(f"{time.time():.6f} : {sensor.data}")
    return _loop

def main():
    sensor = DS18B20Sensor(PATH)
    
    try:
        run(loop(sensor), sensor.setup, sensor.teardown)
        
    except:
        KeyboardInterrupt
        print('Closing')

if __name__ == "__main__":
    main()