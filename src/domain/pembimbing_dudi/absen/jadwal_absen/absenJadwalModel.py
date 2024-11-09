from pydantic import BaseModel
from datetime import date as Date,time as Time
from .....models.absenModel import HariEnum


class AddHariAbsen(BaseModel) :
    hari : HariEnum
    enable : bool = True
    batas_absen_masuk : Time
    batas_absen_pulang : Time
    min_jam_kerja : int

class AddJadwalAbsenBody(BaseModel) :
    tanggal_mulai : Date
    tanggal_berakhir : Date
    hari : list[AddHariAbsen]

class UpdateHariAbsenBody(BaseModel) :
    id : int | None = None
    # hari : HariEnum | None = None
    enable : bool | None = None
    batas_absen_masuk : Time | None = None
    batas_absen_pulang : Time | None = None
    min_jam_kerja : int | None = None


class UpdateJadwalAbsenBody(BaseModel) :
    tanggal_mulai : Date | None = None
    tanggal_berakhir : Date | None = None
    hari : list[UpdateHariAbsenBody] | None = None