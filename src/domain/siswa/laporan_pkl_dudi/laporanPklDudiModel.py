from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiWithoutSiswaAndPembimbing

class ResponseGetLaporanPklDudiPag(PaginationBase) :
    data : list[LaporanPklDudiWithoutSiswaAndPembimbing]

