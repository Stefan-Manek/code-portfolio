#Importing standard libraries
import serial

#Importing custom libraries
from tuppersat.radio import SatRadio


class RunRadio:
    def __init__(self, port):
        """Initialisation"""
        
        self._port_settings = {
            'port' : port,
            'baudrate' : 38400,
            'timeout' : 2,
            }
        self._radio_settings = {
            'address' : 0x54,
            'callsign' : 'TOASTSAT'
            }
                
        # Placeholders for serial, radio
        self._ser = None
        self._radio = None
        

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()

    def setup(self):
        """Setup to open serial port using port details"""
        self._ser = serial.Serial(**self._port_settings)
        self._radio = SatRadio(self._ser, **self._radio_settings)
        self._radio.start()

    def teardown(self):
        """Tearing down by closing serial port and stopping radio"""
        self._radio.stop()
        self._ser.close()
    
    def loop(self):
        """No loop process required"""
        pass

    def send_data(self, message): 
        """Send a data packet via radio"""
        self._radio.send_data_packet(message)
        
    def send_telem(self, telem_dict):
        """Send telemetry packet via radio"""
        self._radio.send_telemetry(**telem_dict)

