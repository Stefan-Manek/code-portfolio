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



def gga_parser(sentence):
    """Parses GGA NMEA sentence and returns fields and values as 
    key-value pairs in dictionary object"""
    
    #Splitting fields into list
    parts = splitstrip(sentence)
    
    #Defining each value
    time = convert_time(check_if_none(parts[1]))
    
    latitude = convert_degrees(check_if_none(parts[2]))
    lat_hemisphere = parts[3]
    
    longitude = convert_degrees(check_if_none(parts[4]))
    lon_hemisphere = parts[5]
    altitude = float(check_if_none(parts[9]))
    hdop = float(check_if_none(parts[8]))
    
    #Defining relevant GGA field keys:
    keys = ('Time', f'Lat ({lat_hemisphere})',
            f'Lon ({lon_hemisphere})', 'Alt (m)', 'HDOP')
    values = (time, latitude, longitude, altitude, hdop)
    
    return dict(zip(keys, values))
