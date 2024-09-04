from pydantic import BaseModel
from datetime import date as Date
from .siswa_model import SiswaBase
from .dudi_model import DudiBase

class LaporanPklSiswaBase(BaseModel) :
    id : int
    tanggal : Date
    keterangan : str
    file_laporan : str
    siswa : SiswaBase
    dudi : DudiBase