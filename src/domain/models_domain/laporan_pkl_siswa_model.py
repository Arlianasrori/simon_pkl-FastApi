from pydantic import BaseModel
from datetime import date as Date
from .siswa_model import SiswaBase
from .dudi_model import DudiBase

class LaporanPklWithoutDudiAndSiswa(BaseModel) :
    id : int
    topik_pekerjaan : str
    rujukan_kompetensi_dasar : str
    dokumentasi :  str | None = None

class LaporanPklSiswaBase(BaseModel) :
    id : int
    topik_pekerjaan : str
    rujukan_kompetensi_dasar : str
    dokumentasi :  str | None = None
    siswa : SiswaBase
    dudi : DudiBase