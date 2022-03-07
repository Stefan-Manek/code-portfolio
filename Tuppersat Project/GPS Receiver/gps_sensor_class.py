import serial
from parse_gga import gga_parser
import contextlib
import time


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
    """Function to run all three processes"""
    setup()
    try:
        while True:
            loop()
    finally:
        teardown()
        

class GpsReceiver:
    """A class representing the GPS receiver."""
    def __init__(self, port):
        """Initialsiation."""
        
        #Detials for openening serial port
        self._serial_details = {'port': port,
                                'baudrate': 9600,
                                'timeout': 1}
        
        #Data attribute
        self._data = None
        
        #NMEA Sentence id
        self._id = 'GGA'
        
    def setup(self):
        """Setup to open serial port using port details"""
        
        self._ser = serial.Serial(**self._serial_details)

    
    def read(self):
        """Listen for GGA sentence, and extract relevant details"""
        
        #Constantly listen for NMEA sentence
        while True:
            sentence = self._ser.readline().decode('ascii')
            sen_id = sentence[3:6]
            
            #Return if GGA sentence
            if sen_id == self._id:
                return gga_parser(sentence)
    
    def update(self):
        """Updating data attribute"""
        self._data = self.read()
        
    def teardown(self):
        """Tearing down by closing serial port"""
        self._ser.close()
        
    @property
    def data(self):
        """Data attribute"""
        return self._data
    
        
PORT = '/dev/ttyACM0'

def loop(sensor):
    """Looping read and update processes"""
    def _loop():
        sensor.update()
        # Printing each update
        print(f"{time.time():.6f} : {sensor._data}")
    return _loop

def main():
    """Creating sensor, run processes and teardown
    after KeybooardInterrupt"""
    sensor = GpsReceiver(PORT)
    
    try:
        run(loop(sensor), sensor.setup, sensor.teardown)
        
    except KeyboardInterrupt:
        print('Closing')

if __name__ == "__main__":
    main()