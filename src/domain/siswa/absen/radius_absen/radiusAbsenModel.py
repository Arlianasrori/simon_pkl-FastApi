from pydantic import BaseModel

class CekRadiusAbsenBody(BaseModel) :
    latitude : float
    longitude : float

class ResponseCekRadius(BaseModel) :
    inside_radius : bool
    distance : float