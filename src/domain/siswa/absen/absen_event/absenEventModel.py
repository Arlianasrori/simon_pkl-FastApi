from pydantic import BaseModel
from enum import Enum

class RadiusBody(BaseModel) :
    latitude : float
    longitude : float

class IzinTelatAbsenEnum(Enum) :
    IZIN = "izin"
    TELAT = "telat"

class ResponseAbsenIzinTelat(BaseModel) :
    msg : str