from pydantic import BaseModel

class AddkoordinatAbsenBody(BaseModel) :
    nama_tempat : str
    latitude : float
    longitude : float
    radius_absen_meter : float

class UpdatekoordinaatAbsenBody(BaseModel) :
    latitude : float | None = None
    longitude : float | None = None
    radius_absen_meter : float | None = None