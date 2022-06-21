import datetime


def splitstrip(s, sep=','):
    """Splits string into constituents and removes whitespace
    """
    return list(v.strip() for v in s.split(sep=sep))


def check_if_none(value):
    """Function that returns None if NMEA field is blank, 
    otherwise returns original value"""
    if value == '':
        return None
    else:
        return value


def convert_time(time_str):
    """Converts string to datetime.time object"""
    #Splitting string into hrs, mins, secs:
    if time_str != None:
        time_parts = [int(time_str[i:i+2]) for i in range(0, 6, 2)]
        time = datetime.time(*time_parts)
        return time
    else:
        return None

def float_none(value):
    """Simple function to return float if value is a string"""
    if value == None:
        return value
    else:
        return float(value)

def convert_degrees(ddmm_string):
    """Converts NMEA lat or long to decimal degrees"""
    #Checking if string is blank:
    if ddmm_string != None:
        #String may begin DDD or DD, finding index to split between D and M:
        split_index = len(ddmm_string) -8
        full_degree = float(ddmm_string[:split_index])
        
        #Minutes remainder converted to degrees and added:
        remainder = float(ddmm_string[split_index:])/60
        dec_deg_value = full_degree + remainder
        return dec_deg_value
    else:
        return None

def get_hemisphere(parts):
    """Extracts Hemispheres from NMEA GGA string"""
    lat_h = check_if_none(parts[3])
    lon_h = check_if_none(parts[5])
    return lat_h, lon_h

def sign_coord(coord, hemisphere):
    if coord==None or hemisphere == None:
        return coord
    elif hemisphere == 'W' or hemisphere == 'S':
        return -1*coord
    else:
        return coord

def gga_parser(sentence):
    """Parses GGA NMEA sentence and returns fields and values in list of
    (key, value) tuples"""
    keys = ('lat_dec_deg', 'lon_dec_deg', 'alt', 'lat_dil')
    if sentence != None:
        #Splitting fields into list
        parts = splitstrip(sentence)
        lat_h, lon_h = get_hemisphere(parts)
        #Defining each value    
        lat = convert_degrees(check_if_none(parts[2]))
        lon = convert_degrees(check_if_none(parts[4]))
        
        lat, lon = sign_coord(lat, lat_h), sign_coord(lon, lon_h)
        altitude = float_none(check_if_none(parts[9]))
        hdop = float_none(check_if_none(parts[8]))
        
        #Defining relevant GGA field keys:
        
        values = (lat, lon, altitude, hdop)
        
        return list(zip(keys, values))
    else:
        values = [None for i in keys]
        return list(zip(keys, values))

def gps_altitude(sentence):
    """Parses GGA NMEA sentence and returns altitude,
    with label in tuple e.g:
    >>> ('alt', 121.5)"""
    if sentence != None:
    	#Splitting fields into list
    	parts = splitstrip(sentence)
    	altitude = float_none(check_if_none(parts[9]))
    else:
        altitude = None
    return ('alt', altitude)
