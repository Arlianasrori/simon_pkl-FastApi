from pydantic import BaseModel
from datetime import date as Date,time as Time
from .....models.absenModel import HariEnum


class AddHariAbsen(BaseModel) :
    hari : HariEnum
    batas_absen_masuk : Time
    batas_absen_pulang : Time

class AddJadwalAbsenBody(BaseModel) :
    tanggal_mulai : Date
    tanggal_berakhir : Date
    hari : list[AddHariAbsen]

class UpdateHariAbsenBody(BaseModel) :
    id : int
    batas_absen_masuk : Time | None = None
    batas_absen_pulang : Time | None = None

class UpdateJadwalAbsenBody(BaseModel) :
    tanggal_mulai : Date | None = None
    tanggal_berakhir : Date | None = None
    hari : list[UpdateHariAbsenBody] | None = None