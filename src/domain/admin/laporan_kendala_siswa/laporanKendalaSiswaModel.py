from datetime import date as Date
from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_kendala_model import LaporanKendalaWithSiswa

class ResponseLaporanKendalaSiswaPag(PaginationBase) :
    data : list[LaporanKendalaWithSiswa] = []

class FilterLaporanPklKendalaSiswaQuery(BaseModel) :
    id_siswa : int | None = None
    tanggal : Date | None = None
    month : int | None = None
    year : int | None = None
