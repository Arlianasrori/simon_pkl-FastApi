from pydantic import BaseModel
from datetime import time as Time,date as Date
from ...models.absenModel import StatusAbsenEnum,StatusAbsenMasukKeluarEnum,StatusOtherAbsenEnum,HariEnum
from .siswa_model import SiswaBase,SiswaWithDudi,SiswaWithDudiWithOutKelasJurusan
from .dudi_model import DudiBase
from datetime import date as Date,time as Time

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
    status_absen_masuk : str
    status_absen_keluar : str
    status : StatusAbsenEnum

class AbsenWithSiswa(AbsenBase) :
    siswa : SiswaBase

class AbsenWithSiswaDudi(AbsenBase) :
    siswa : SiswaWithDudiWithOutKelasJurusan

class SiswaWithAbsen(SiswaBase) :
    absen : list[AbsenBase]
    
class MoreAbsen(AbsenBase) :
    siswa : SiswaBase
    keterangan_absen_masuk : KeteranganAbsenMasuk | None = None
    keterangan_absen_pulang : KeteranganAbsenKeluar | None = None


# jadwal absen
class JadwalAbsenBase(BaseModel) :
    id : int
    id_dudi : int
    tanggal_mulai : Date
    tanggal_berakhir : Date
    selisih_tanggal_day : int

class HariAbsenBase(BaseModel) :
    id : int
    hari : HariEnum
    batas_absen_masuk : Time
    batas_absen_pulang : Time

class JadwalAbsenWithHari(JadwalAbsenBase) :
    hari : list[HariAbsenBase] = []

# koordinat absen
class koordinatAbsenBase(BaseModel) :
    id : int
    nama_tempat : str
    latitude : float
    longitude : float
    radius_absen_meter : int

class KoordinatAbsenWithDudi(koordinatAbsenBase) :
    dudi : DudiBase