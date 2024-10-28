from pydantic import BaseModel
from datetime import date as Date
from .dudi_model import DudiBase
from .pembimbing_dudi_model import PembimbingDudiBase

class LaporanPklDudiBase(BaseModel) :
    id : int
    tanggal : Date
    topik_pekerjaan : str
    rujukan_kompetensi_dasar : str
    file_laporan : str | None = None
    dudi : DudiBase
    pembimbing_dudi : PembimbingDudiBase

class LaporanPklDudiWithOut(BaseModel) :
    id : int
    tanggal : Date
    topik_pekerjaan : str
    rujukan_kompetensi_dasar : str
    file_laporan : str | None = None

class LaporanPklDudiWithoutSiswaAndPembimbing(LaporanPklDudiWithOut) :
    dudi : DudiBase

