from pydantic import BaseModel
from enum import Enum
from ....models_domain.absen_model import JadwalAbsenBase,HariAbsenBase

class JenisAbsenEnum(Enum) :
    MASUK = "masuk"
    PULANG = "pulang"

class StatusAbsenMasukEnum(Enum) :
    HADIR = "hadir"
    TELAT = "telat"

class StatusAbsenPulangEnum(Enum) :
    HADIR = "hadir"
    TELAT = "telat"
    DILUAR_RADIUS = "diluar_radius"
    IZIN = "izin"


class RadiusBody(BaseModel) :
    latitude : float
    longitude : float

class ResponseCekAbsen(BaseModel) :
    canAbsen : bool
    jenis_absen : JenisAbsenEnum | None = None
    jenis_absen_masuk : StatusAbsenMasukEnum | None = None
    jenis_absen_pulang : StatusAbsenPulangEnum | None = None

class ResponseJadwalAbsenToday(JadwalAbsenBase) :
    hari : HariAbsenBase
