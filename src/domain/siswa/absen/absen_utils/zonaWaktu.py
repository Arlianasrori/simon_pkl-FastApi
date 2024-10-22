# from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime

# from geopy.geocoders import Nominatim
# import pytz

async def get_timezone_from_coordinates(lat, lon):
    if 95 <= lon < 105:
        return timezone("Asia/Jakarta")
    elif 105 <= lon < 120:
        return timezone("Asia/Makassar")
    elif 120 <= lon < 135:
        return timezone("Asia/Jayapura")
    else:
        return None

async def get_local_time(zona_waktu : str): 
    print(zona_waktu) 
    return datetime.now(zona_waktu)


# async def get_timezone_from_coordinates(latitude: float, longitude: float):
#     tf = TimezoneFinder(in_memory=True)
#     zona_waktu_string = tf.certain_timezone_at(lat=latitude, lng=longitude)
    
#     if zona_waktu_string is None:
#         return None
    
#     return timezone(zona_waktu_string)