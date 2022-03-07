import time

def unpack(buffer ):
    """ Unpacks MSB -ordered buffer of bytes into an unsigned integer.
    Note: buffer must be a bytes -like object or a list of integers in the
    range [0, 255].
    Usage:
    >>> unpack ([0x01 , 0x00])
    256
    >>> unpack ([0x10 , 0x00])
    4096
    >>> unpack ([0xFF , 0xFF , 0xFF])
    16777215
    """
    _buffer = reversed(bytearray(buffer))
    return sum(_byte << (_i * 8) for _i, _byte in enumerate(_buffer ))

def read_calibration_constants(bus, addr):
    """Reads and unpacks calibration constants from pressure sensor
    from the listed addresses
    
    Returns constants as a list of integers."""
    #List of addresses for cal constants
    POSITIONS = [0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC]
    #Including None so no 0 index value:
    cal_constants = [None]
    for pos in POSITIONS:
        c1bytes = bus.read_i2c_block_data(addr, pos, 2)
        const = unpack(c1bytes)
        cal_constants.append(const)
    return cal_constants

def read_adc(bus, addr, cmd):
    """Inputs: Bus object, address of sensor, and cmd string
    specifying temperature or pressure to be read.
    
    Reads pressure or temperature ADC values depending on cmd input.
    
    Returns integer value for temp or press"""
    # send temperature ADC command and pause for response
    if cmd == 't':
        adc = 0x58
    elif cmd == 'p':
        adc = 0x48
        
    bus.write_byte(addr , adc)
    time.sleep(0.05)
    # read the ADC values
    adc_bytes = bus.read_i2c_block_data(addr , 0x00 , 3)
    # unpack value as integer
    adc_int = unpack(adc_bytes)
    return adc_int

def compute_pressure(t_adc, p_adc, cal_list):
    """Converts ADC value to temp or press as centicelsius or hectobar 
    respectively using calibration constants.
    
    Uses algorithm specified in sensor datasheet."""
    D1, D2 = p_adc, t_adc
    dT = D2 - (cal_list[5]*(2**8))
    temperature = 2000 + (dT*cal_list[6])/(2**23)
    offset = (cal_list[2]*(2**16)) + (cal_list[4]*dT)/(2**7)
    sensitivity = cal_list[1]*(2**15) + (cal_list[3]*dT) / (2**8)
    pressure = (((D1*sensitivity)/(2**21))  - offset) / (2**15)
    
    return temperature, pressure

def read_pressure(bus, addr, cal_list):
    """Reads temperature and pressure from sensor and converts
    to integer values"""
    t_adc = read_adc(bus, addr, 't')
    p_adc = read_adc(bus, addr, 'p')
    temperature, pressure = compute_pressure(t_adc, p_adc, cal_list)
    return temperature, pressure

def format_temp_pres(temp, pres):
    """Converts centicelsius and hectobar to celsius and mbar"""
    temp_degC = temp/100
    pres_mbar = pres/100
    return temp_degC, pres_mbar

def read_ms5611(bus, address, cal_constants):
    """Reads temperature and pressure from
    sensor and returns as celsius and mbar."""
    temperature, pressure = read_pressure(bus, address, cal_constants)
    t_degC, p_mbar = format_temp_pres(temperature, pressure)
    return t_degC, p_mbar
