from pydantic import BaseModel,field_validator
from datetime import date as Date
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_siswa_model import LaporanPklWithoutDudiAndSiswa
from babel.dates import format_date
from babel import Locale
from enum import Enum

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

class EnumJenisLaporan(Enum) :
    laporanSiswa = "laporanSiswa"
    kendala = "kendala"

class ResponseGetLaporanPklSiswaAndKendala(BaseModel) :
    id : int
    tanggal : str
    jenis_laporan : EnumJenisLaporan

    @field_validator("tanggal",mode="before")
    def validateTanggal(cls,v) :
        locale_id = Locale('id', 'ID')
        print(v)
        print(format_date(v, format="EEEE, d MMMM yyyy", locale=locale_id))
        return format_date(v, format="EEEE, d MMMM yyyy", locale=locale_id)
