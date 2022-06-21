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


def read_adc(bus, addr):
    """Inputs: Bus object, address of sensor, and cmd string
    specifying temperature or pressure to be read.
    
    Reads pressure or temperature ADC values depending on cmd input.
    
    Returns integer value for temp or press"""
    # send temperature ADC command and pause for response cmd == 'p':        
    bus.write_byte(addr , 0xF5)
    time.sleep(0.05)
    # read the ADC values
    adc_bytes = bus.read_byte(addr)
    # unpack value as integer
    adc_int = adc_bytes * 256
    return adc_int

def compute_humidity(h_adc):
    """Converts ADC value to temp or press as centicelsius or hectobar 
    respectively using calibration constants.
    
    Uses algorithm specified in sensor datasheet."""
    D3 = h_adc
    rel_hum = -600 + 12500 * D3 / (2**16)
    return rel_hum

def read_MS8607(bus, addr):
    """Reads temperature and pressure from sensor and converts
    to integer values"""
    h_adc = read_adc(bus, addr)
    rel_hum = compute_humidity(h_adc)
    return rel_hum

