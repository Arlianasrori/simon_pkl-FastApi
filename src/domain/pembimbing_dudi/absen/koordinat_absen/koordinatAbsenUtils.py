import math
async def is_valid_coordinate(latitude, longitude):
    lat = float(latitude)
    lon = float(longitude)
    
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        return True
    else:
        return False
async def is_valid_latitude(latitude):
    lat = float(latitude)
    
    if -90 <= lat <= 90:
        return True
    else:
        return False
    
async def is_valid_longitude(longitude):
    lon = float(longitude)
    
    if -180 <= lon <= 180:
        return True
    else:
        return False
    
def calculate_radius(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius Bumi dalam meter

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c

    return round(distance, 2) 