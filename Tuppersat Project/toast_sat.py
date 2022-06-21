#Importing standard libraries
import time
from datetime import datetime as dt
import logging
#################################################


#Importing gps airborne mode
from tuppersat.airborne import set_airborne

#Importing utility functions
from class_utils import catch_and_suppress

#Importing sensor classes
from gps.gps_sensor_class import GpsReceiver
from temperature_sensors.temp_class import DS18B20Sensor
from pressure_sensors.pressure_class import MS5611Sensor
from humidity_sensor.pressure_class import MS5611ExtSensor
from humidity_sensor.humidity_class import MS8607Sensor
from ozone_sensor.ozone_class import OzoneSensor, OZONE_ADDRESS_3

#Importing run classes
from run_sensors import RunSensors
from radio.radio_class import RunRadio

#Importing processes
from handle_telem import HandleTelemetry
from handle_data import HandleData
from store_data import StoreData
from run_processes import RunProcesses

#################################################

#Starting logger
FMT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'
LOG_DIR = '/home/pi/logs/'


################################################

#Defining gps port and setting to airborne mode
GPS_PORT   = '/dev/ttyACM0'
set_airborne(GPS_PORT)

#Defining ports + addresses

TEMP_PATH1 = '/sys/bus/w1/devices/28-00000deac472/w1_slave'
TEMP_PATH2 = '/sys/bus/w1/devices/28-0120424fab9f/w1_slave'
RADIO_PATH = '/dev/ttyAMA0'
PRESS_INT_ADDR = 0x77
PRESS_EXT_ADDR = 0x76
HUM_ADDR = 0x40

#Ozone sensor inputs
COLLECT_NUMBER   = 20
IIC_MODE         = 0x01
#####################################################

        
    
def main():
    """Runs threads for all specified sensors.
    Extracts attributes from housekeeping and data sensors,
    combines to packets and sends via radio.
    
    Stores and timestamps all sensor data to local file every second.
    
    Threads stopped by KeyboardInterrupt"""
    log_filename = f"{LOG_DIR}{dt.now():%Y-%m-%d-%H-%M-%S}_toastsat.log"
    logging.basicConfig(filename =log_filename,
                    level=logging.INFO,
                    format = FMT)
    
    # Dictionary of sensor objects
    sensors = {'gps'     : GpsReceiver(GPS_PORT),
               'temp1'   : DS18B20Sensor(TEMP_PATH1),
               'temp2'   : DS18B20Sensor(TEMP_PATH2),
               'pressure': MS5611Sensor(PRESS_INT_ADDR),
               'p_ext'   : MS5611ExtSensor(PRESS_EXT_ADDR),
               'hum'     : MS8607Sensor(HUM_ADDR),
               'ozone'   : OzoneSensor(IIC_MODE,
                                     OZONE_ADDRESS_3,
                                     COLLECT_NUMBER)
               }
    
    with catch_and_suppress(KeyboardInterrupt):
        with RunSensors(sensors):
            with RunRadio(RADIO_PATH) as run_radio:
                processes = [
                    HandleTelemetry(sensors, run_radio._radio),
                    HandleData(sensors, run_radio._radio),
                    StoreData(sensors)
                    ]
                time.sleep(1)
                with RunProcesses(processes):
                    #wait indefinitely
                    while True: time.sleep(0.1)
    print('Finished')
        
if __name__ == '__main__':
    main()
