from pydantic import BaseModel
from datetime import date as Date
from .siswa_model import SiswaWithDudiWithOutKelasJurusan

class LaporankendalaBase(BaseModel) :
    id : int
    tanggal : Date | None = None
    kendala : str
    file_laporan : str | None = None
    deskripsi : str | None = None

class LaporanKendalaWithSiswa(LaporankendalaBase) :
    siswa : SiswaWithDudiWithOutKelasJurusan