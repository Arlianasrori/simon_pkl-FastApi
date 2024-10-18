from pydantic import BaseModel
from datetime import date as Date
from .siswa_model import SiswaWithDudiWithOutKelasJurusan

class LaporankendalaDudiBase(BaseModel) :
    id : int
    id_siswa : int
    id_pembimbing_dudi : int
    tanggal : Date | None = None
    kendala : str
    file_laporan : str | None = None
    deskripsi : str | None = None

class LaporanKendalaDudiWithSiswa(LaporankendalaDudiBase) :
    siswa : SiswaWithDudiWithOutKelasJurusan