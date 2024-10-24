from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from datetime import date as Date


class ResponseLaporanPklDudiPag(PaginationBase) :
    data : list[LaporanPklDudiBase] = []

class FilterLaporanPklDudiQuery(BaseModel) :
    tanggal : Date | None = None
    month : int | None = None
    year : int | None = None