from pydantic import BaseModel
from datetime import date as Date
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_siswa_model import LaporanPklWithoutDudiAndSiswa

class AddLaporanPklSiswaBody(BaseModel):
    tanggal : Date
    topik_pekerjaan : str
    rujukan_kompetensi_dasar : str

class UpdateLaporanPklSiswaBody(BaseModel):
    tanggal : Date | None = None
    topik_pekerjaan : str | None = None
    rujukan_kompetensi_dasar : str | None = None

class ResponseGetLaporanPklSiswaPag(PaginationBase) :
    data : list[LaporanPklWithoutDudiAndSiswa]

class FilterLaporan(BaseModel) :
    month : int | None = None
    year : int | None = None
