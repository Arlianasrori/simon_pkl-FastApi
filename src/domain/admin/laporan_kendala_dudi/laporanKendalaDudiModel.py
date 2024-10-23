from datetime import date as Date
from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_kendala_dudi_model import LaporanKendalaDudiWithSiswaPembimbingDudi

class ResponseLaporanPklDudiPag(PaginationBase) :
    data : list[LaporanKendalaDudiWithSiswaPembimbingDudi] = []

class FilterLaporanPklKendalaDudiQuery(BaseModel) :
    id_siswa : int | None = None
    tanggal : Date | None = None
    month : int | None = None
    year : int | None = None