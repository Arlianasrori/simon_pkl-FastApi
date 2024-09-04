from pydantic import BaseModel
from datetime import time as Time,date as Date
from ...models.absenModel import StatusAbsenEnum,StatusAbsenMasukKeluarEnum,StatusOtherAbsenEnum
from .siswa_model import SiswaBase

class KeteranganAbsenMasuk(BaseModel) :
    id : int
    note : str
    status_izin : StatusOtherAbsenEnum

class KeteranganAbsenKeluar(BaseModel) :
    id : int
    note : str
    status_izin : StatusOtherAbsenEnum

class AbsenBase(BaseModel):
    id : int
    id_absen_jadwal : int
    id_siswa : int
    tanggal : Date
    absen_masuk : Time
    absen_pulang : Time
    status_absen_masuk : StatusAbsenMasukKeluarEnum | None = None
    status_absen_pulang : StatusAbsenMasukKeluarEnum | None = None
    foto : str
    status : StatusAbsenEnum
class SiswaWithAbsen(SiswaBase) :
    absen : list[AbsenBase]
    
class MoreAbsen(AbsenBase) :
    siswa : SiswaBase
    keterangan_absen_masuk : KeteranganAbsenMasuk | None = None
    keterangan_absen_pulang : KeteranganAbsenKeluar | None = None