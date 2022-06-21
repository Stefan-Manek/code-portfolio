import serial
import time
import logging

class GpsReceiver:
    """A class representing the GPS receiver."""
    def __init__(self, port):
        """Initialsiation."""
        
        #Detials for openening serial port
        self._serial_details = {'port': port,
                                'baudrate': 9600,
                                'timeout': 1}
        self._ser = None
        
        #Data attribute
        self._data = None
        
        #NMEA Sentence id
        self._id = 'GGA'
        
        self._logger = logging.getLogger(__name__)
        
    def setup(self):
        """Setup to open serial port using port details"""
        try:
            #Open serial port
            self._ser = serial.Serial(**self._serial_details)
            
        except (serial.SerialException, AttributeError) as exc:
            self._logger.exception(type(exc).__name__)
            self._data = None
            self.teardown()
            time.sleep(60)

    
    def read(self):
        """Listen for GGA sentence, and extract relevant details"""
        #Constantly listen for NMEA sentence
        try:
            while True:
                sentence = self._ser.readline().decode('ascii')
                sen_id = sentence[3:6]
                        
                #Return if GGA sentence
                if sen_id == self._id:
                    return sentence
        except (serial.SerialException, AttributeError) as exc:
            self._logger.info(type(exc).__name__)
            self._data = None
            self.teardown()
            time.sleep(60)
                
        
    def update(self):
        """Updating data attribute"""
        self._data = self.read()
        
    def teardown(self):
        """Tearing down by closing serial port"""
        if self._ser != None:
            self._ser.close()
        pass
        
    @property
    def data(self):
        """Data attribute"""
        return self._data
    

