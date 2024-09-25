from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase
from datetime import date as Date


class ResponseLaporanPklSiswaPag(PaginationBase) :
    data : list[LaporanPklSiswaBase] = []

class FilterLaporanPklSiswaQuery(BaseModel) :
    id_siswa : int | None = None
    tanggal : Date | None = None
    month : int | None = None
    year : int | None = None