from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase

class ResponseLaporanPklDudiPag(PaginationBase) :
    data : list[LaporanPklDudiBase] = []