## Flight Directory

> Contains final Python implementation of the full on-board software for TOAST-Sat.

Each directory contains scripts relating to specific subsytem on-board TOAST-Sat.

- **gps:** Includes module containing class representation of the u-blox GPS receiver. Contains utility module for parsing raw NMEA strings to extract relevant data.
- **humidity_sensor:** Contains class modules representing both Humidity and Pressure+Temperature sensors for the MS8607-02BA01 PHT sensor, and associated utility modules.
- **ozone_sensor:** Contains library file from manufacturer and class to read concentration value from the sensor.
- **pressure_sensors:** Contains module for running MS5611 pressure sensor.
- **radio:** Contains radio class used to transmit data and telemetry packets to ground station.
- **temperature_sensors:** Contains class-based implementation of DS18B20 sensor and associated utility module.

Other included modules and their function within the software are as follows:
- class_utils.py: Contains functions to read and update sensor classes in the background.
- thread_utils.py: Contains functions to start, loop and stop sensor threads.
- handle_data.py: Module that gathers data from all sensors and compiles it into data packets with relevant formatting.
- handle_telem.py: Module that gathers data from all sensors and compiles it into telemetry packets with relevant formatting.
- store_data.py: Module that gathers data from all sensors and compiles it into onboard data products.
- run_processes.py: Contains class that runs all process as threads.
- run_sensors.py: Contains class that runs all sensors as threads.
- toast_sat.py: Main script that runs all TOAST-Sat software as required.
