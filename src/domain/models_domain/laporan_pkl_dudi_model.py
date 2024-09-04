from pydantic import BaseModel
from datetime import date as Date
from .siswa_model import SiswaBase
from .dudi_model import DudiBase
from .pembimbing_dudi_model import PembimbingDudiBase

class LaporanPklDudiBase(BaseModel) :
    id : int
    tanggal : Date
    keterangan : str
    file_laporan : str
    siswa : SiswaBase
    dudi : DudiBase
    pembimbing_dudi : PembimbingDudiBase