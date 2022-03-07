

def format_temperature(lines):
    """Reads temperature from sensor file and formats to degrees C. """
    #Finding position of equals sign:
    equals_pos = lines[1].find('t=')
    #Reading temperature as a string
    t_string = lines[1][equals_pos + 2:]
    #Returning as Celsius
    return float(t_string) / 1000


def read_ds18b20(path):
    """ Read DS18B20 temperature as float in Celsius."""
    with open(path, 'r') as sensor:
        lines = sensor.readlines()
    t_degC = format_temperature(lines)
    return t_degC



        
