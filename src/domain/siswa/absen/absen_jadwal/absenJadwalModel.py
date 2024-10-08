from pydantic import BaseModel
from enum import Enum
from ....models_domain.absen_model import JadwalAbsenBase,HariAbsenBase

class JenisAbsenEnum(Enum) :
    MASUK = "masuk"
    PULANG = "pulang"
    TELAT = "telat"
    DILUAR_RADIUS = "diluar_radius"
    IZIN = "izin"


class RadiusBody(BaseModel) :
    latitude : float
    longitude : float

class ResponseCekAbsen(BaseModel) :
    canAbsen : bool
    jenis_absen : JenisAbsenEnum | None = None
