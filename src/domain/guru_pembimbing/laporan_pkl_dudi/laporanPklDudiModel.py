from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase

class Filter(BaseModel) :
    id_dudi : int | None = None
    id_siswa : int | None = None

class ResponseLaporanPklDudiPag(PaginationBase) :
    data : list[LaporanPklDudiBase] = []